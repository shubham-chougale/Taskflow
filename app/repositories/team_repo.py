from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.team import Team


class TeamRepository:
    """Repository for team data access operations"""
    
    async def get_by_id(self, db: AsyncSession, team_id: UUID) -> Team | None:
        """Get team by ID"""
        result = await db.execute(
            select(Team).where(Team.id == team_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_name(self, db: AsyncSession, name: str) -> Team | None:
        """Get team by name"""
        result = await db.execute(
            select(Team).where(Team.name == name)
        )
        return result.scalar_one_or_none()
    
    async def create(self, db: AsyncSession, name: str) -> Team:
        """Create a new team"""
        team = Team(name=name)
        db.add(team)
        await db.commit()
        await db.refresh(team)
        return team
    
    async def update(self, db: AsyncSession, team_id: UUID, name: str) -> Team | None:
        """Update team by ID"""
        team = await self.get_by_id(db, team_id)
        if not team:
            return None
        
        team.name = name
        await db.commit()
        await db.refresh(team)
        return team
    
    async def delete(self, db: AsyncSession, team_id: UUID) -> bool:
        """Delete team by ID"""
        team = await self.get_by_id(db, team_id)
        if not team:
            return False
        
        await db.delete(team)
        await db.commit()
        return True
    
    async def list(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Team]:
        """List all teams with pagination"""
        result = await db.execute(
            select(Team).offset(skip).limit(limit)
        )
        return list(result.scalars().all())
