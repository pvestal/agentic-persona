"""
Authentication and Authorization Service
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
import secrets
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Configuration
SECRET_KEY = secrets.token_urlsafe(32)  # In production, use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Bearer token
security = HTTPBearer()

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[str] = None

class AuthService:
    """Handles authentication and authorization"""
    
    def __init__(self):
        self.pwd_context = pwd_context
        
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return self.pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def create_refresh_token(self, data: dict):
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def decode_token(self, token: str) -> TokenData:
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            user_id: str = payload.get("user_id")
            
            if email is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            return TokenData(email=email, user_id=user_id)
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def create_api_key(self, user_id: str, name: str = "default") -> str:
        """Create API key for user"""
        # Generate secure random key
        api_key = f"echo_{secrets.token_urlsafe(32)}"
        
        # In production, store this in database with user_id and name
        # For now, we'll encode user info in the key
        data = {
            "user_id": user_id,
            "name": name,
            "created": datetime.utcnow().isoformat(),
            "type": "api_key"
        }
        
        # Create a JWT-like API key
        encoded_key = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
        return f"echo_{encoded_key}"
    
    def validate_api_key(self, api_key: str) -> Dict[str, Any]:
        """Validate API key"""
        if not api_key.startswith("echo_"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key format"
            )
        
        try:
            # Extract the JWT part
            key_part = api_key[5:]  # Remove "echo_" prefix
            payload = jwt.decode(key_part, SECRET_KEY, algorithms=[ALGORITHM])
            
            if payload.get("type") != "api_key":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid API key"
                )
            
            return payload
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )

# Dependency injection
auth_service = AuthService()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    token = credentials.credentials
    token_data = auth_service.decode_token(token)
    
    # In production, fetch user from database
    # For now, return token data
    return {
        "email": token_data.email,
        "user_id": token_data.user_id
    }

async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Get current user if authenticated, None otherwise"""
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None

# Permission decorators
class Permissions:
    """Role-based permissions"""
    
    @staticmethod
    def require_admin(current_user: dict = Depends(get_current_user)):
        """Require admin role"""
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        return current_user
    
    @staticmethod
    def require_agent_access(agent_name: str):
        """Require access to specific agent"""
        async def check_permission(current_user: dict = Depends(get_current_user)):
            # Check if user has access to this agent
            allowed_agents = current_user.get("allowed_agents", [])
            
            if agent_name not in allowed_agents and current_user.get("role") != "admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access to agent '{agent_name}' denied"
                )
            
            return current_user
        
        return check_permission

# Rate limiting
from collections import defaultdict
from datetime import datetime
import asyncio

class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.requests = defaultdict(list)
        self.cleanup_task = None
    
    async def check_rate_limit(
        self, 
        key: str, 
        max_requests: int = 60, 
        window_seconds: int = 60
    ) -> bool:
        """Check if request is within rate limit"""
        now = datetime.now()
        window_start = now - timedelta(seconds=window_seconds)
        
        # Clean old requests
        self.requests[key] = [
            req_time for req_time in self.requests[key] 
            if req_time > window_start
        ]
        
        # Check limit
        if len(self.requests[key]) >= max_requests:
            return False
        
        # Add current request
        self.requests[key].append(now)
        return True
    
    async def cleanup_old_requests(self):
        """Periodic cleanup of old request records"""
        while True:
            await asyncio.sleep(300)  # Clean every 5 minutes
            
            cutoff = datetime.now() - timedelta(minutes=10)
            for key in list(self.requests.keys()):
                self.requests[key] = [
                    req_time for req_time in self.requests[key]
                    if req_time > cutoff
                ]
                
                if not self.requests[key]:
                    del self.requests[key]

rate_limiter = RateLimiter()

# Rate limit dependency
async def check_rate_limit(
    current_user: dict = Depends(get_current_user),
    max_requests: int = 60
):
    """Rate limit check dependency"""
    key = current_user.get("user_id", "anonymous")
    
    if not await rate_limiter.check_rate_limit(key, max_requests):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )
    
    return current_user