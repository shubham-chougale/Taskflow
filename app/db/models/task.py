import uuid
from enum import Enum

from sqlalchemy import (
    Column,
    String,
    Text,
    ForeignKey,
    Enum as SqlEnum,
    Boolean,
    DateTime,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class TaskStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    status = Column(
        SqlEnum(TaskStatus, name="taskstatus"),
        nullable=False,
        server_default=TaskStatus.OPEN.value,
    )

    # Ownership
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Team scoping
    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=False)

    # Soft delete
    is_deleted = Column(Boolean, nullable=False, server_default="false")

    # Timestamps
    created_at = Column(DateTime(timezone=False), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=False),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    created_by = relationship("User", foreign_keys=[created_by_id])
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    team = relationship("Team")
