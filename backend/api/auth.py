"""
Authentication API endpoints
Login, logout, token refresh, and registration
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.database.models import User, AuditLog
from backend.database.connection import get_async_db
from backend.auth.security import (
    security_manager,
    get_current_user,
    get_current_active_user
)
from backend.schemas.auth import (
    Token,
    TokenRefresh,
    UserCreate,
    UserResponse,
    PasswordChange,
    PasswordReset
)
from backend.schemas.common import MessageResponse

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    request: Request,
    db: AsyncSession = Depends(get_async_db)
):
    """Register a new user"""
    # Check if user already exists
    result = await db.execute(
        select(User).where(
            (User.username == user_data.username) | 
            (User.email == user_data.email)
        )
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        if existing_user.username == user_data.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Validate password strength
    password_validation = security_manager.validate_password_strength(user_data.password)
    if not password_validation["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Password does not meet requirements", "errors": password_validation["errors"]}
        )
    
    # Create new user
    hashed_password = security_manager.get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        is_active=True,
        is_superuser=False
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Log registration
    audit_log = AuditLog(
        user_id=new_user.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        action="user_registered",
        resource_type="user",
        resource_id=str(new_user.id),
        request_method=request.method,
        request_path=request.url.path,
        response_status=200
    )
    db.add(audit_log)
    await db.commit()
    
    return new_user


@router.post("/login", response_model=Token)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_db)
):
    """Login and receive access token"""
    # Find user
    result = await db.execute(
        select(User).where(User.username == form_data.username)
    )
    user = result.scalar_one_or_none()
    
    if not user or not security_manager.verify_password(form_data.password, user.hashed_password):
        # Log failed login attempt
        if user:
            audit_log = AuditLog(
                user_id=user.id,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                action="login_failed",
                resource_type="auth",
                request_method=request.method,
                request_path=request.url.path,
                response_status=401,
                details={"reason": "invalid_password"}
            )
            db.add(audit_log)
            await db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    # Check rate limit
    if not await security_manager.check_rate_limit(str(user.id), "login"):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts"
        )
    
    # Create tokens
    access_token = security_manager.create_access_token(subject=user.id)
    refresh_token = security_manager.create_refresh_token(subject=user.id)
    
    # Update last login
    user.last_login_at = datetime.utcnow()
    await db.commit()
    
    # Log successful login
    audit_log = AuditLog(
        user_id=user.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        action="login_success",
        resource_type="auth",
        request_method=request.method,
        request_path=request.url.path,
        response_status=200
    )
    db.add(audit_log)
    await db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_data: TokenRefresh,
    db: AsyncSession = Depends(get_async_db)
):
    """Refresh access token using refresh token"""
    try:
        # Decode refresh token
        payload = await security_manager.decode_token(token_data.refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        user_id = payload.get("sub")
        
        # Get user
        result = await db.execute(
            select(User).where(User.id == user_id, User.is_active == True)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Create new tokens
        access_token = security_manager.create_access_token(subject=user.id)
        refresh_token = security_manager.create_refresh_token(subject=user.id)
        
        # Blacklist old refresh token
        await security_manager.blacklist_token(token_data.refresh_token)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Logout and invalidate tokens"""
    # Get token from header
    authorization = request.headers.get("authorization", "")
    token = authorization.replace("Bearer ", "")
    
    if token:
        # Blacklist the access token
        await security_manager.blacklist_token(token)
    
    # Log logout
    audit_log = AuditLog(
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        action="logout",
        resource_type="auth",
        request_method=request.method,
        request_path=request.url.path,
        response_status=200
    )
    db.add(audit_log)
    await db.commit()
    
    return {"message": "Successfully logged out"}


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Change user password"""
    # Verify current password
    if not security_manager.verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Validate new password
    password_validation = security_manager.validate_password_strength(password_data.new_password)
    if not password_validation["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Password does not meet requirements", "errors": password_validation["errors"]}
        )
    
    # Update password
    current_user.hashed_password = security_manager.get_password_hash(password_data.new_password)
    current_user.updated_at = datetime.utcnow()
    
    # Log password change
    audit_log = AuditLog(
        user_id=current_user.id,
        action="password_changed",
        resource_type="user",
        resource_id=str(current_user.id),
        response_status=200
    )
    db.add(audit_log)
    
    await db.commit()
    
    return {"message": "Password successfully changed"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information"""
    return current_user