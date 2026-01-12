from uuid import UUID
from typing import Optional
from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.task import Task, TaskStatus


class TaskRepository:
    """Repository for task data access operations"""
    
    async def get_by_id(self, db: AsyncSession, task_id: UUID) -> Task | None:
        """Get task by ID"""
        result = await db.execute(
            select(Task).where(
                Task.id == task_id,
                Task.is_deleted == False
            )
        )
        return result.scalar_one_or_none()
    
    async def create(
        self,
        db: AsyncSession,
        title: str,
        description: str | None,
        created_by_id: UUID,
        assigned_to_id: UUID | None,
        team_id: UUID,
        status: TaskStatus = TaskStatus.OPEN
    ) -> Task:
        """Create a new task"""
        task = Task(
            title=title,
            description=description,
            created_by_id=created_by_id,
            assigned_to_id=assigned_to_id,
            team_id=team_id,
            status=status
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return task
    
    async def update(self, db: AsyncSession, task_id: UUID, **kwargs) -> Task | None:
        """Update task by ID"""
        task = await self.get_by_id(db, task_id)
        if not task:
            return None
        
        for key, value in kwargs.items():
            if hasattr(task, key) and value is not None:
                setattr(task, key, value)
        
        await db.commit()
        await db.refresh(task)
        return task
    
    async def delete(self, db: AsyncSession, task_id: UUID) -> bool:
        """Soft delete task by ID"""
        task = await self.get_by_id(db, task_id)
        if not task:
            return False
        
        task.is_deleted = True
        await db.commit()
        return True
    
    async def list(
        self,
        db: AsyncSession,
        filters: dict,
        skip: int = 0,
        limit: int = 10
    ) -> list[Task]:
        """List tasks with filters and pagination"""
        query = select(Task).where(Task.is_deleted == False)
        
        # Apply filters
        if filters.get("status"):
            query = query.where(Task.status == filters["status"])
        
        if filters.get("assignee_id"):
            query = query.where(Task.assigned_to_id == filters["assignee_id"])
        
        if filters.get("team_id"):
            query = query.where(Task.team_id == filters["team_id"])
        
        if filters.get("created_by_id"):
            query = query.where(Task.created_by_id == filters["created_by_id"])
        
        if filters.get("user_id"):  # For member role - tasks created by or assigned to user
            query = query.where(
                or_(
                    Task.created_by_id == filters["user_id"],
                    Task.assigned_to_id == filters["user_id"]
                )
            )
        
        # Pagination
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_team(self, db: AsyncSession, team_id: UUID, skip: int = 0, limit: int = 10) -> list[Task]:
        """Get all tasks for a team"""
        return await self.list(
            db,
            filters={"team_id": team_id},
            skip=skip,
            limit=limit
        )
    
    async def get_by_assignee(self, db: AsyncSession, assignee_id: UUID, skip: int = 0, limit: int = 10) -> list[Task]:
        """Get all tasks assigned to a user"""
        return await self.list(
            db,
            filters={"assignee_id": assignee_id},
            skip=skip,
            limit=limit
        )
    
    async def get_by_creator(self, db: AsyncSession, creator_id: UUID, skip: int = 0, limit: int = 10) -> list[Task]:
        """Get all tasks created by a user"""
        return await self.list(
            db,
            filters={"created_by_id": creator_id},
            skip=skip,
            limit=limit
        )
