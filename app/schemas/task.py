from datetime import datetime
from uuid import UUID
from typing import Optional
from enum import Enum
from pydantic import BaseModel
from app.db.models.task import TaskStatus


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    assignee_id: Optional[UUID] = None


class TaskCreate(TaskBase):
    pass


class TaskRead(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    status: TaskStatus

    created_by_id: UUID
    assigned_to_id: Optional[UUID]
    team_id: UUID

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TaskResponse(BaseModel):
    id: UUID
    title: str
    description: str | None
    status: TaskStatus
    created_by_id: UUID
    assigned_to_id: UUID | None
    team_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    assignee_id: Optional[UUID] = None
