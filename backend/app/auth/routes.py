"""
Authentication API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.auth.schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
    RefreshTokenRequest,
    PasswordChange
)
from app.auth.service import AuthService
from app.auth.dependencies import get_current_active_user, require_admin
from app.auth.models import User

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    
    - **email**: User email (must be unique)
    - **password**: User password (min 8 characters)
    - **full_name**: Optional full name
    - **role**: User role (viewer, operator, admin)
    """
    user = AuthService.create_user(db, user_data)
    return user


@router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login with email and password.
    
    Returns access token and refresh token.
    
    - **email**: User email
    - **password**: User password
    """
    user = AuthService.authenticate_user(db, login_data)
    tokens = AuthService.create_tokens(user)
    return tokens


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: RefreshTokenRequest
):
    """
    Refresh access token using refresh token.
    
    - **refresh_token**: Valid refresh token
    """
    tokens = AuthService.refresh_access_token(refresh_data.refresh_token)
    return tokens


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user information.
    
    Requires valid access token.
    """
    return current_user


@router.post("/change-password", response_model=UserResponse)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Change current user password.
    
    - **current_password**: Current password
    - **new_password**: New password (min 8 characters)
    """
    user = AuthService.change_password(
        db,
        current_user,
        password_data.current_password,
        password_data.new_password
    )
    return user


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    List all users (admin only).
    
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get user by ID (admin only).
    
    - **user_id**: User UUID
    """
    user = AuthService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user
