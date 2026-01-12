from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreate
from app.core.security import verify_password, create_access_token, hash_password
from app.repositories.user_repo import UserRepository
from app.core.exceptions import AuthenticationError, ValidationError, ConflictError
from app.core.logging import logger


class AuthService:
    """Service for authentication and authorization business logic"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository()
    
    async def authenticate(self, email: str, password: str) -> TokenResponse:
        """Authenticate user and return JWT token"""
        logger.info(f"Authentication attempt for email: {email}")
        
        user = await self.user_repo.get_by_email(self.db, email)
        if not user or not verify_password(password, user.password_hash):
            logger.warning(f"Authentication failed for email: {email}")
            raise AuthenticationError("Invalid credentials")
        
        access_token = create_access_token(subject=str(user.id))
        logger.info(f"User authenticated successfully: {user.id}")
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer"
        )
    
    async def get_current_user(self, token: str) -> User:
        """Get current user from JWT token"""
        from app.core.security import decode_access_token
        
        payload = decode_access_token(token)
        if payload is None:
            raise AuthenticationError("Invalid or expired token")
        
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise AuthenticationError("Invalid token payload")
        
        user = await self.user_repo.get_by_id(self.db, user_id)
        if user is None:
            raise AuthenticationError("User not found")
        
        return user
    
    async def register_user(self, user_data: UserCreate) -> User:
        """Register a new user"""
        logger.info(f"Registration attempt for email: {user_data.email}")
        
        # Check if user already exists
        existing_user = await self.user_repo.get_by_email(self.db, user_data.email)
        if existing_user:
            logger.warning(f"Registration failed - email already exists: {user_data.email}")
            raise ConflictError("Email already registered")
        
        # Hash password
        password_hash = hash_password(user_data.password)
        
        # Create user
        user = await self.user_repo.create(
            db=self.db,
            email=user_data.email,
            password_hash=password_hash,
            role=user_data.role
        )
        
        logger.info(f"User registered successfully: {user.id}")
        return user
