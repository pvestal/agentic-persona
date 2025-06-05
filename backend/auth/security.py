"""
Authentication and security implementation
JWT tokens, password hashing, and authorization
"""

import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union
import logging

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import redis.asyncio as redis

from backend.config import settings
from backend.database.models import User
from backend.database.connection import get_async_db

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


class SecurityManager:
    """Manages authentication, authorization, and security features"""
    
    def __init__(self):
        self.redis_client = None
        self._initialize_redis()
    
    def _initialize_redis(self):
        """Initialize Redis connection for token blacklist and rate limiting"""
        try:
            self.redis_client = redis.from_url(
                settings.get_redis_url(),
                encoding="utf-8",
                decode_responses=True
            )
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            self.redis_client = None
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash password using bcrypt"""
        return pwd_context.hash(password)
    
    def create_access_token(self, subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode = {
            "exp": expire,
            "sub": str(subject),
            "type": "access",
            "iat": datetime.utcnow()
        }
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY.get_secret_value(),
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    
    def create_refresh_token(self, subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT refresh token"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode = {
            "exp": expire,
            "sub": str(subject),
            "type": "refresh",
            "iat": datetime.utcnow()
        }
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY.get_secret_value(),
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    
    async def decode_token(self, token: str) -> Dict[str, Any]:
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY.get_secret_value(),
                algorithms=[settings.ALGORITHM]
            )
            
            # Check if token is blacklisted
            if self.redis_client:
                is_blacklisted = await self.redis_client.get(f"blacklist:{token}")
                if is_blacklisted:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token has been revoked"
                    )
            
            return payload
            
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
    
    async def blacklist_token(self, token: str, expire_time: int = None):
        """Add token to blacklist"""
        if not self.redis_client:
            logger.warning("Redis not available, cannot blacklist token")
            return
        
        try:
            # Decode token to get expiration
            payload = jwt.decode(
                token,
                settings.SECRET_KEY.get_secret_value(),
                algorithms=[settings.ALGORITHM],
                options={"verify_exp": False}
            )
            
            # Calculate TTL until token expires
            exp = payload.get("exp", 0)
            ttl = expire_time or max(exp - datetime.utcnow().timestamp(), 0)
            
            if ttl > 0:
                await self.redis_client.setex(f"blacklist:{token}", int(ttl), "1")
                
        except Exception as e:
            logger.error(f"Failed to blacklist token: {e}")
    
    def generate_api_key(self, length: int = 32) -> str:
        """Generate secure API key"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    async def validate_api_key(self, api_key: str, db: AsyncSession) -> Optional[User]:
        """Validate API key and return user"""
        result = await db.execute(
            select(User).where(User.api_key == api_key, User.is_active == True)
        )
        user = result.scalar_one_or_none()
        
        if user:
            # Update last request time
            user.last_request_at = datetime.utcnow()
            await db.commit()
        
        return user
    
    async def check_rate_limit(self, user_id: str, request_type: str = "api") -> bool:
        """Check if user has exceeded rate limit"""
        if not settings.RATE_LIMIT_ENABLED or not self.redis_client:
            return True
        
        try:
            # Define rate limit windows
            windows = {
                "minute": (60, settings.RATE_LIMIT_PER_MINUTE),
                "hour": (3600, settings.RATE_LIMIT_PER_HOUR),
                "day": (86400, settings.RATE_LIMIT_PER_DAY)
            }
            
            current_time = int(datetime.utcnow().timestamp())
            
            for window_name, (window_size, limit) in windows.items():
                key = f"rate_limit:{user_id}:{request_type}:{window_name}:{current_time // window_size}"
                
                # Increment counter
                count = await self.redis_client.incr(key)
                
                # Set expiration on first request
                if count == 1:
                    await self.redis_client.expire(key, window_size)
                
                # Check if limit exceeded
                if count > limit:
                    logger.warning(f"Rate limit exceeded for user {user_id} in {window_name} window")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            # Fail open - allow request if rate limiting fails
            return True
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password meets security requirements"""
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if not re.search(r"[A-Z]", password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not re.search(r"[a-z]", password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not re.search(r"\d", password):
            errors.append("Password must contain at least one digit")
        
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            errors.append("Password must contain at least one special character")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "strength": self._calculate_password_strength(password)
        }
    
    def _calculate_password_strength(self, password: str) -> str:
        """Calculate password strength score"""
        score = 0
        
        # Length
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        if len(password) >= 16:
            score += 1
        
        # Character variety
        if re.search(r"[A-Z]", password):
            score += 1
        if re.search(r"[a-z]", password):
            score += 1
        if re.search(r"\d", password):
            score += 1
        if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            score += 1
        
        # Map score to strength
        if score < 3:
            return "weak"
        elif score < 5:
            return "medium"
        elif score < 7:
            return "strong"
        else:
            return "very_strong"


# Global security manager instance
security_manager = SecurityManager()


# Dependency functions
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db)
) -> User:
    """Get current authenticated user from JWT token"""
    try:
        payload = await security_manager.decode_token(token)
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        
        # Get user from database
        result = await db.execute(
            select(User).where(User.id == user_id, User.is_active == True)
        )
        user = result.scalar_one_or_none()
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Update last login
        user.last_login_at = datetime.utcnow()
        await db.commit()
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Ensure user is active"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Ensure user is superuser"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


class RateLimitMiddleware:
    """Middleware for rate limiting"""
    
    async def __call__(self, request: Request, call_next):
        # Extract user ID from various sources
        user_id = None
        
        # Try JWT token
        if "authorization" in request.headers:
            try:
                token = request.headers["authorization"].replace("Bearer ", "")
                payload = await security_manager.decode_token(token)
                user_id = payload.get("sub")
            except:
                pass
        
        # Try API key
        if not user_id and "x-api-key" in request.headers:
            api_key = request.headers["x-api-key"]
            # This would need database lookup in production
            user_id = f"api_key:{api_key[:8]}"
        
        # Use IP as fallback
        if not user_id:
            user_id = f"ip:{request.client.host}"
        
        # Check rate limit
        if not await security_manager.check_rate_limit(user_id):
            return HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        
        response = await call_next(request)
        return response


import re  # Add this import at the top of the file