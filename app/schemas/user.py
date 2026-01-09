from pydantic import BaseModel, EmailStr
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    MEMBER = "MEMBER"


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: UserRole = UserRole.MEMBER
