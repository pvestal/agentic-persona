"""
Authentication API routes
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt
import bcrypt

from config.settings import settings

router = APIRouter()
security = HTTPBearer()

# In production, these would be in a database
USERS_DB = {
    "demo@example.com": {
        "password_hash": bcrypt.hashpw(b"demo123", bcrypt.gensalt()),
        "name": "Demo User",
        "role": "user"
    }
}

class LoginRequest(BaseModel):
    email: str
    password: str

class UserProfile(BaseModel):
    name: str
    communication_style: str = "balanced"
    vip_contacts: list = []
    preferences: Dict[str, Any] = {}

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]

def create_token(user_email: str) -> str:
    """Create JWT token"""
    payload = {
        "sub": user_email,
        "exp": datetime.utcnow() + timedelta(hours=24),
        "iat": datetime.utcnow()
    }
    
    # In production, use a proper secret key
    secret_key = settings.openai_api_key or "your-secret-key"
    return jwt.encode(payload, secret_key, algorithm="HS256")

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Verify JWT token"""
    token = credentials.credentials
    
    try:
        secret_key = settings.openai_api_key or "your-secret-key"
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """User login"""
    # Check if user exists
    if request.email not in USERS_DB:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user = USERS_DB[request.email]
    
    # Verify password
    if not bcrypt.checkpw(request.password.encode(), user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create token
    token = create_token(request.email)
    
    return TokenResponse(
        access_token=token,
        expires_in=86400,  # 24 hours
        user={
            "email": request.email,
            "name": user["name"],
            "role": user["role"]
        }
    )

@router.post("/register")
async def register(email: str, password: str, name: str):
    """Register new user"""
    if email in USERS_DB:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Hash password
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    
    # Store user
    USERS_DB[email] = {
        "password_hash": password_hash,
        "name": name,
        "role": "user"
    }
    
    # Create initial profile
    profile = UserProfile(name=name)
    
    return {
        "success": True,
        "message": "User registered successfully",
        "user": {
            "email": email,
            "name": name
        }
    }

@router.get("/profile")
async def get_profile(current_user: str = Depends(verify_token)):
    """Get user profile"""
    if current_user not in USERS_DB:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = USERS_DB[current_user]
    
    # Load profile from file or database
    from pathlib import Path
    import json
    
    profile_path = Path("user-preferences.json")
    if profile_path.exists():
        with open(profile_path, 'r') as f:
            profile_data = json.load(f)
    else:
        profile_data = {
            "name": user["name"],
            "communication_style": "balanced",
            "vip_contacts": [],
            "preferences": {}
        }
    
    return profile_data

@router.put("/profile")
async def update_profile(
    profile: UserProfile,
    current_user: str = Depends(verify_token)
):
    """Update user profile"""
    from pathlib import Path
    import json
    
    # Save profile
    profile_data = profile.dict()
    profile_data["email"] = current_user
    profile_data["updated_at"] = datetime.now().isoformat()
    
    with open("user-preferences.json", 'w') as f:
        json.dump(profile_data, f, indent=2)
    
    return {
        "success": True,
        "message": "Profile updated successfully"
    }

@router.post("/logout")
async def logout(current_user: str = Depends(verify_token)):
    """User logout"""
    # In a real implementation, you might want to blacklist the token
    return {
        "success": True,
        "message": "Logged out successfully"
    }

@router.get("/verify")
async def verify_auth(current_user: str = Depends(verify_token)):
    """Verify authentication status"""
    return {
        "authenticated": True,
        "user": current_user
    }