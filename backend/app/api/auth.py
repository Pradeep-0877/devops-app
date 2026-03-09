from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from pydantic import BaseModel
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    decode_token
)
from app.core.ldap_auth import ldap_auth
from app.models.schemas import Token, LoginRequest, UserResponse, UserCreate
from app.models.repositories import UserRepository
from loguru import logger

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint - supports both LDAP and local authentication"""
    
    # Try LDAP authentication first if enabled
    if settings.LDAP_ENABLED:
        ldap_user = ldap_auth.authenticate(form_data.username, form_data.password)
        
        if ldap_user:
            # Check if user exists in local database
            user = await UserRepository.get_user_by_username(form_data.username)
            
            # Create local user record if doesn't exist
            if not user:
                user_create = UserCreate(
                    username=ldap_user['username'],
                    email=ldap_user.get('email'),
                    full_name=ldap_user.get('full_name') or ldap_user.get('display_name'),
                    password="",  # No password for LDAP users
                    is_active=True
                )
                user = await UserRepository.create_user(user_create, auth_source="ldap")
            
            # Update last login
            await UserRepository.update_last_login(user.id)
            
            # Create tokens
            access_token = create_access_token(
                data={"sub": user.username, "user_id": user.id}
            )
            refresh_token = create_refresh_token(
                data={"sub": user.username, "user_id": user.id}
            )
            
            logger.info(f"User {form_data.username} logged in via LDAP")
            
            return Token(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer"
            )
    
    # Fall back to local authentication
    user = await UserRepository.get_user_by_username(form_data.username)
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Failed login attempt for user: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Update last login
    await UserRepository.update_last_login(user.id)
    
    # Create tokens
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id}
    )
    refresh_token = create_refresh_token(
        data={"sub": user.username, "user_id": user.id}
    )
    
    logger.info(f"User {form_data.username} logged in locally")
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


class RefreshTokenRequest(BaseModel):
    refresh_token: str


@router.post("/refresh", response_model=Token)
async def refresh_token(body: RefreshTokenRequest):
    """Refresh access token using refresh token"""
    
    try:
        payload = decode_token(body.refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        username = payload.get("sub")
        user_id = payload.get("user_id")
        
        # Create new tokens
        new_access_token = create_access_token(
            data={"sub": username, "user_id": user_id}
        )
        new_refresh_token = create_refresh_token(
            data={"sub": username, "user_id": user_id}
        )
        
        return Token(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not refresh token"
        )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_create: UserCreate):
    """Register a new local user"""
    
    # Check if user already exists
    existing_user = await UserRepository.get_user_by_username(user_create.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Create user
    user = await UserRepository.create_user(user_create, auth_source="local")
    
    logger.info(f"New user registered: {user.username}")
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_admin=user.is_admin,
        created_at=user.created_at,
        last_login=user.last_login
    )
