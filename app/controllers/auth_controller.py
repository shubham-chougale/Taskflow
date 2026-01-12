from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreate
from app.services.auth_service import AuthService
from app.core.logging import logger


class AuthController:
    """Controller for authentication endpoints"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.auth_service = AuthService(db)
    
    async def login(self, request: LoginRequest) -> TokenResponse:
        """Handle user login"""
        logger.info(f"Login request for email: {request.email}")
        try:
            token_response = await self.auth_service.authenticate(
                email=request.email,
                password=request.password
            )
            return token_response
        except Exception as e:
            logger.error(f"Login failed for email: {request.email}, error: {str(e)}")
            raise
    
    async def register(self, request: UserCreate) -> dict:
        """Handle user registration"""
        logger.info(f"Registration request for email: {request.email}")
        try:
            user = await self.auth_service.register_user(request)
            return {
                "id": str(user.id),
                "email": user.email,
                "role": user.role
            }
        except Exception as e:
            logger.error(f"Registration failed for email: {request.email}, error: {str(e)}")
            raise
    
    async def get_current_user(self, current_user: User) -> dict:
        """Get current authenticated user info"""
        return {
            "id": str(current_user.id),
            "email": current_user.email,
            "role": current_user.role,
            "team_id": str(current_user.team_id) if current_user.team_id else None
        }
