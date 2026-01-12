from uuid import UUID
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.models.user import User
from app.schemas.user import UserRole
from app.core.security import decode_access_token
from app.core.exceptions import AuthenticationError, AuthorizationError


def get_token_from_header(request: Request) -> str:
    """Extract Bearer token from Authorization header"""
    authorization = request.headers.get("Authorization")
    if not authorization:
        raise AuthenticationError("Authorization header missing")
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AuthenticationError("Invalid authorization header format. Expected: Bearer <token>")
    
    return parts[1]


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get current authenticated user from JWT token"""
    token = get_token_from_header(request)
    
    payload = decode_access_token(token)
    if payload is None:
        raise AuthenticationError("Invalid or expired token")

    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise AuthenticationError("Invalid token payload")

    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise AuthenticationError("User not found")

    return user 

def require_role(*roles: UserRole):
    """Dependency to require specific user roles"""
    def checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise AuthorizationError("Insufficient permissions")
        return current_user

    return checker

def require_same_team(resource_team_id: UUID, user: User):
    """Check if user has access to team resource"""
    if user.role == UserRole.ADMIN:
        return

    if user.team_id != resource_team_id:
        raise AuthorizationError("Access restricted to your team")
    
def require_task_ownership(task_owner_id: UUID, user: User):
    """Check if user owns the task"""
    if user.role == UserRole.ADMIN:
        return

    if user.id != task_owner_id:
        raise AuthorizationError("You do not own this resource")
    
def require_can_create_task(
    current_user: User = Depends(get_current_user),
) -> User:
    """Check if user can create tasks"""
    if current_user.role not in (
        UserRole.ADMIN,
        UserRole.MANAGER,
    ):
        raise AuthorizationError("Not allowed to create task")

    if current_user.role != UserRole.ADMIN and not current_user.team_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must belong to a team",
        )

    return current_user
