from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.user import User
from app.db.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate, TaskRead, TaskResponse
from app.db.models.task import TaskStatus
from app.services.task_service import TaskService
from app.core.logging import logger


class TaskController:
    """Controller for task endpoints"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.task_service = TaskService(db)
    
    async def create_task(self, request: TaskCreate, current_user: User) -> TaskRead:
        """Handle task creation"""
        logger.info(f"Task creation request by user: {current_user.id}")
        try:
            task = await self.task_service.create_task(request, current_user)
            return TaskRead.model_validate(task)
        except Exception as e:
            logger.error(f"Task creation failed by user: {current_user.id}, error: {str(e)}")
            raise
    
    async def list_tasks(
        self,
        current_user: User,
        status: TaskStatus | None = None,
        assignee_id: UUID | None = None,
        skip: int = 0,
        limit: int = 10
    ) -> list[TaskResponse]:
        """Handle task listing"""
        logger.info(f"Task list request by user: {current_user.id}")
        try:
            tasks = await self.task_service.list_tasks(
                current_user=current_user,
                status=status,
                assignee_id=assignee_id,
                skip=skip,
                limit=limit
            )
            return [TaskResponse.model_validate(task) for task in tasks]
        except Exception as e:
            logger.error(f"Task list failed for user: {current_user.id}, error: {str(e)}")
            raise
    
    async def update_task(
        self,
        task_id: UUID,
        request: TaskUpdate,
        current_user: User
    ) -> TaskRead:
        """Handle task update"""
        logger.info(f"Task update request: {task_id} by user: {current_user.id}")
        try:
            task = await self.task_service.update_task(task_id, request, current_user)
            return TaskRead.model_validate(task)
        except Exception as e:
            logger.error(f"Task update failed: {task_id} by user: {current_user.id}, error: {str(e)}")
            raise
    
    async def delete_task(self, task_id: UUID, current_user: User) -> None:
        """Handle task deletion"""
        logger.info(f"Task deletion request: {task_id} by user: {current_user.id}")
        try:
            await self.task_service.delete_task(task_id, current_user)
        except Exception as e:
            logger.error(f"Task deletion failed: {task_id} by user: {current_user.id}, error: {str(e)}")
            raise
