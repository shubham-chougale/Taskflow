import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base
from app.schemas.user import UserRole


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)

    role = Column(
        ENUM(UserRole, name="userrole", create_type=False),
        nullable=False,
    )

    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    team_id = Column(UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True)

    team = relationship("Team", back_populates="users")
