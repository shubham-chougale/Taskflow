from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.user import User
from app.schemas.user import UserRole


class UserRepository:
    """Repository for user data access operations"""
    
    async def get_by_id(self, db: AsyncSession, user_id: UUID) -> User | None:
        """Get user by ID"""
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, db: AsyncSession, email: str) -> User | None:
        """Get user by email"""
        result = await db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def create(self, db: AsyncSession, email: str, password_hash: str, role: UserRole, team_id: UUID | None = None) -> User:
        """Create a new user"""
        user = User(
            email=email,
            password_hash=password_hash,
            role=role,
            team_id=team_id
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    
    async def update(self, db: AsyncSession, user_id: UUID, **kwargs) -> User | None:
        """Update user by ID"""
        user = await self.get_by_id(db, user_id)
        if not user:
            return None
        
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        await db.commit()
        await db.refresh(user)
        return user
    
    async def delete(self, db: AsyncSession, user_id: UUID) -> bool:
        """Delete user by ID"""
        user = await self.get_by_id(db, user_id)
        if not user:
            return False
        
        await db.delete(user)
        await db.commit()
        return True
    
    async def get_by_team(self, db: AsyncSession, team_id: UUID) -> list[User]:
        """Get all users in a team"""
        result = await db.execute(
            select(User).where(User.team_id == team_id)
        )
        return list(result.scalars().all())
    
    async def get_by_role(self, db: AsyncSession, role: UserRole) -> list[User]:
        """Get all users with a specific role"""
        result = await db.execute(
            select(User).where(User.role == role)
        )
        return list(result.scalars().all())
