from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.db.session import get_db
from app.db.models.user import User
from app.schemas.task import TaskCreate, TaskRead, TaskResponse
from app.schemas.task import TaskUpdate
from app.core.dependencies import get_current_user, require_role
from app.db.models.user import UserRole
from app.db.models.task import TaskStatus
from app.controllers.task_controller import TaskController

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post(
    "",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(UserRole.ADMIN, UserRole.MANAGER))]
)
async def create_task(
    data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new task"""
    controller = TaskController(db)
    return await controller.create_task(data, current_user)


@router.get("/", response_model=list[TaskResponse])
async def list_tasks(
    status: TaskStatus | None = Query(None),
    assignee_id: UUID | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List tasks with role-based filtering and pagination"""
    controller = TaskController(db)
    return await controller.list_tasks(
        current_user=current_user,
        status=status,
        assignee_id=assignee_id,
        skip=skip,
        limit=limit
    )


@router.put(
    "/{task_id}",
    response_model=TaskRead,
    dependencies=[Depends(require_role(UserRole.ADMIN, UserRole.MANAGER))]
)
async def update_task(
    task_id: UUID,
    data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a task"""
    controller = TaskController(db)
    return await controller.update_task(task_id, data, current_user)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role(UserRole.ADMIN, UserRole.MANAGER))]
)
async def delete_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a task"""
    controller = TaskController(db)
    await controller.delete_task(task_id, current_user)
    return None
