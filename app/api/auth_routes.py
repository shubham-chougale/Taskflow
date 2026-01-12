from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.auth import LoginRequest, TokenResponse
from app.db.session import get_db
from app.db.models.user import User
from app.core.dependencies import get_current_user
from app.schemas.user import UserCreate
from app.controllers.auth_controller import AuthController

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Login endpoint - authenticates user and returns JWT token"""
    controller = AuthController(db)
    return await controller.login(request)


@router.get("/me")
async def read_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current authenticated user info"""
    controller = AuthController(db)
    return await controller.get_current_user(current_user)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user"""
    controller = AuthController(db)
    return await controller.register(data)