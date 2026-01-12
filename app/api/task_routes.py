from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from sqlalchemy import or_
from app.db.session import get_db
from app.db.models.task import Task
from app.db.models.user import User
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.core.dependencies import get_current_user, require_role
from app.db.models.user import UserRole
from app.schemas.task import TaskResponse
from app.db.models.task import TaskStatus
from app.core.dependencies import require_can_create_task
from datetime import datetime 

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
    current_user: User = Depends(require_can_create_task),
):
    # Ensure user belongs to a team
    if current_user.role == UserRole.Manager and not data.assignee_id:
        raise HTTPException(
            status_code=400,
            detail="Manager must assign task to a user"
        )
    
    if current_user.role != UserRole.Admin  and not current_user.team_id:
        raise HTTPException(
            status_code=400,
            detail="User is not assigned to any team"
        )

    # Validate assignee belongs to same team
    assignee = None
    if data.assignee_id:
        if current_user.role == UserRole.ADMIN:
            result = await db.execute(
                select(User).where(User.id == data.assignee_id)
            )
        else:
            result = await db.execute(
            select(User).where(
                User.id == data.assignee_id,
                User.team_id == current_user.team_id,
            )
        )    
        assignee = result.scalar_one_or_none()

        if not assignee:
            raise HTTPException(
                status_code=400, detail="Invalid assignee")

    team_id = assignee.team_id if current_user.role == UserRole.ADMIN else current_user.team_id
    
    task = Task(
        title=data.title,
        description=data.description,
        assigned_to_id=data.assignee_id,
        created_by_id=current_user.id,
        team_id = team_id,
        status=TaskStatus.OPEN,
    )

    db.add(task)
    await db.commit()
    await db.refresh(task)

    return task

@router.get("/", response_model=list[TaskResponse])
async def list_tasks(
    status: TaskStatus | None = Query(None),
    assignee_id: UUID | None = Query(None),
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Task)

    # Role-based visibility
    if current_user.role == UserRole.ADMIN:
        pass
    elif current_user.role == UserRole.MANAGER:
        query = query.where(Task.team_id == current_user.team_id)
    else:  # MEMBER
        query = query.where(
                or_(
                    Task.created_by_id == current_user.id,
                    Task.assigned_to_id == current_user.id,
                )
            )


    # Filters
    if status:
        query = query.where(Task.status == status)

    if assignee_id:
        if current_user.role == UserRole.MEMBER:
            raise HTTPException(
                status_code=403,
                detail="Members cannot filter by assignee"
            )
        # MANAGER: assignee must belong to same team
        if current_user.role == UserRole.MANAGER:
            result = await db.execute(
                select(User).where(
                    User.id == assignee_id,
                    User.team_id == current_user.team_id
                )
            )
            assignee = result.scalar_one_or_none()

            if not assignee:
                raise HTTPException(
                    status_code=403,
                    detail="Assignee not in your team"
                )
        query = query.where(Task.assigned_to_id == assignee_id)

    # Pagination
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    tasks = result.scalars().all()

    return tasks

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
    result = await db.execute(
        select(Task).where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # MANAGER can update only their team tasks
    if current_user.role == UserRole.MANAGER:
        if task.team_id != current_user.team_id:
            raise HTTPException(status_code=403, detail="Not allowed")

    # Validate assignee
    if data.assignee_id:
        if current_user.role == UserRole.ADMIN:
            result = await db.execute(
                select(User).where(User.id == data.assignee_id)
            )
        else:
            result = await db.execute(
                select(User).where(
                    User.id == data.assignee_id,
                    User.team_id == current_user.team_id
                )
            )

        assignee = result.scalar_one_or_none()
        if not assignee:
            raise HTTPException(status_code=400, detail="Invalid assignee")

        task.assigned_to_id = data.assignee_id

    # Update fields
    if data.title is not None:
        task.title = data.title
    if data.description is not None:
        task.description = data.description
    if data.status is not None:
        task.status = data.status

    task.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(task)

    return task

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
    result = await db.execute(
        select(Task).where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # MANAGER can delete only their team tasks
    if current_user.role == UserRole.MANAGER:
        if task.team_id != current_user.team_id:
            raise HTTPException(status_code=403, detail="Not allowed")

    await db.delete(task)
    await db.commit()

    return None
