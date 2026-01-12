from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.user import User
from app.repositories.user_repo import UserRepository
from app.core.exceptions import NotFoundError, ValidationError
from app.core.logging import logger


class UserService:
    """Service for user business logic"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository()
    
    async def get_user_by_id(self, user_id: UUID) -> User:
        """Get user by ID"""
        user = await self.user_repo.get_by_id(self.db, user_id)
        if not user:
            raise NotFoundError("User not found")
        return user
    
    async def get_user_by_email(self, email: str) -> User:
        """Get user by email"""
        user = await self.user_repo.get_by_email(self.db, email)
        if not user:
            raise NotFoundError("User not found")
        return user
    
    async def get_users_by_team(self, team_id: UUID) -> list[User]:
        """Get all users in a team"""
        users = await self.user_repo.get_by_team(self.db, team_id)
        return users
    
    async def update_user_team(self, user_id: UUID, team_id: UUID | None) -> User:
        """Update user's team assignment"""
        user = await self.user_repo.get_by_id(self.db, user_id)
        if not user:
            raise NotFoundError("User not found")
        
        updated_user = await self.user_repo.update(self.db, user_id, team_id=team_id)
        logger.info(f"User team updated: {user_id} -> team: {team_id}")
        return updated_user
