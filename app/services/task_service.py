from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.task import Task, TaskStatus
from app.db.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate
from app.schemas.user import UserRole
from app.repositories.task_repo import TaskRepository
from app.repositories.user_repo import UserRepository
from app.core.exceptions import AuthorizationError, NotFoundError, ValidationError
from app.core.logging import logger
from datetime import datetime


class TaskService:
    """Service for task business logic"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.task_repo = TaskRepository()
        self.user_repo = UserRepository()
    
    async def create_task(self, task_data: TaskCreate, current_user: User) -> Task:
        """Create a new task with RBAC validation"""
        logger.info(f"Task creation attempt by user: {current_user.id}")
        
        # Validate user can create tasks
        if current_user.role not in (UserRole.ADMIN, UserRole.MANAGER):
            logger.warning(f"User {current_user.id} attempted to create task without permission")
            raise AuthorizationError("Not allowed to create task")
        
        # Validate team assignment for non-admin users
        if current_user.role != UserRole.ADMIN and not current_user.team_id:
            raise ValidationError("User must belong to a team")
        
        # Validate assignee
        assignee = None
        if task_data.assignee_id:
            if current_user.role == UserRole.ADMIN:
                assignee = await self.user_repo.get_by_id(self.db, task_data.assignee_id)
            else:
                # Manager can only assign to team members
                assignee = await self.user_repo.get_by_id(self.db, task_data.assignee_id)
                if not assignee or assignee.team_id != current_user.team_id:
                    raise ValidationError("Invalid assignee - must be a team member")
            
            if not assignee:
                raise ValidationError("Invalid assignee")
        
        # Determine team_id
        if current_user.role == UserRole.ADMIN:
            team_id = assignee.team_id if assignee else current_user.team_id
        else:
            team_id = current_user.team_id
        
        if not team_id:
            raise ValidationError("Team ID is required")
        
        # Create task
        task = await self.task_repo.create(
            db=self.db,
            title=task_data.title,
            description=task_data.description,
            created_by_id=current_user.id,
            assigned_to_id=task_data.assignee_id,
            team_id=team_id,
            status=TaskStatus.OPEN
        )
        
        logger.info(f"Task created successfully: {task.id} by user: {current_user.id}")
        return task
    
    async def list_tasks(
        self,
        current_user: User,
        status: Optional[TaskStatus] = None,
        assignee_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 10
    ) -> list[Task]:
        """List tasks with role-based filtering"""
        logger.info(f"Task list request by user: {current_user.id}, role: {current_user.role}")
        
        filters = {}
        
        # Role-based visibility
        if current_user.role == UserRole.ADMIN:
            # Admin can see all tasks
            if assignee_id:
                filters["assignee_id"] = assignee_id
        elif current_user.role == UserRole.MANAGER:
            # Manager can see team tasks
            if not current_user.team_id:
                raise ValidationError("Manager must belong to a team")
            filters["team_id"] = current_user.team_id
            
            # Validate assignee filter for manager
            if assignee_id:
                assignee = await self.user_repo.get_by_id(self.db, assignee_id)
                if not assignee or assignee.team_id != current_user.team_id:
                    raise AuthorizationError("Assignee not in your team")
                filters["assignee_id"] = assignee_id
        else:  # MEMBER
            # Member can only see their own tasks
            filters["user_id"] = current_user.id
            if assignee_id:
                raise AuthorizationError("Members cannot filter by assignee")
        
        # Apply status filter
        if status:
            filters["status"] = status
        
        tasks = await self.task_repo.list(
            db=self.db,
            filters=filters,
            skip=skip,
            limit=limit
        )
        
        logger.info(f"Retrieved {len(tasks)} tasks for user: {current_user.id}")
        return tasks
    
    async def update_task(self, task_id: UUID, task_data: TaskUpdate, current_user: User) -> Task:
        """Update a task with RBAC validation"""
        logger.info(f"Task update attempt: {task_id} by user: {current_user.id}")
        
        # Get task
        task = await self.task_repo.get_by_id(self.db, task_id)
        if not task:
            raise NotFoundError("Task not found")
        
        # Validate access
        if current_user.role not in (UserRole.ADMIN, UserRole.MANAGER):
            raise AuthorizationError("Not allowed to update task")
        
        if current_user.role == UserRole.MANAGER:
            if task.team_id != current_user.team_id:
                raise AuthorizationError("Not allowed to update tasks outside your team")
        
        # Validate assignee if provided
        if task_data.assignee_id:
            if current_user.role == UserRole.ADMIN:
                assignee = await self.user_repo.get_by_id(self.db, task_data.assignee_id)
            else:
                assignee = await self.user_repo.get_by_id(self.db, task_data.assignee_id)
                if not assignee or assignee.team_id != current_user.team_id:
                    raise ValidationError("Invalid assignee - must be a team member")
            
            if not assignee:
                raise ValidationError("Invalid assignee")
        
        # Prepare update data
        update_data = {}
        if task_data.title is not None:
            update_data["title"] = task_data.title
        if task_data.description is not None:
            update_data["description"] = task_data.description
        if task_data.status is not None:
            update_data["status"] = task_data.status
        if task_data.assignee_id is not None:
            update_data["assigned_to_id"] = task_data.assignee_id
        
        update_data["updated_at"] = datetime.utcnow()
        
        # Update task
        updated_task = await self.task_repo.update(self.db, task_id, **update_data)
        
        logger.info(f"Task updated successfully: {task_id}")
        return updated_task
    
    async def delete_task(self, task_id: UUID, current_user: User) -> None:
        """Delete a task with RBAC validation"""
        logger.info(f"Task deletion attempt: {task_id} by user: {current_user.id}")
        
        # Get task
        task = await self.task_repo.get_by_id(self.db, task_id)
        if not task:
            raise NotFoundError("Task not found")
        
        # Validate access
        if current_user.role not in (UserRole.ADMIN, UserRole.MANAGER):
            raise AuthorizationError("Not allowed to delete task")
        
        if current_user.role == UserRole.MANAGER:
            if task.team_id != current_user.team_id:
                raise AuthorizationError("Not allowed to delete tasks outside your team")
        
        # Soft delete
        await self.task_repo.delete(self.db, task_id)
        
        logger.info(f"Task deleted successfully: {task_id}")
    
    async def validate_task_access(self, task: Task, user: User) -> None:
        """Validate if user has access to a task"""
        if user.role == UserRole.ADMIN:
            return
        
        if user.role == UserRole.MANAGER:
            if task.team_id != user.team_id:
                raise AuthorizationError("Access restricted to your team")
        else:  # MEMBER
            if task.created_by_id != user.id and task.assigned_to_id != user.id:
                raise AuthorizationError("Access restricted to your tasks")
