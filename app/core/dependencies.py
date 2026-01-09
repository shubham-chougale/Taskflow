from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.models.user import User
from app.schemas.user import UserRole
from app.core.security import decode_access_token 
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user 

def require_role(*roles: UserRole):
    def checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return checker

def require_same_team(resource_team_id: int, user: User):
    if user.role == UserRole.ADMIN:
        return

    if user.team_id != resource_team_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to your team",
        )
    
def require_task_ownership(task_owner_id: int, user: User):
    if user.role == UserRole.ADMIN:
        return

    if user.id != task_owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not own this resource",
        )
    
def require_can_create_task(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role not in (
        UserRole.ADMIN,
        UserRole.MANAGER,
        UserRole.MEMBER,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to create task",
        )

    if current_user.role != UserRole.ADMIN and not current_user.team_id:
        raise HTTPException(
            status_code=400,
            detail="User must belong to a team",
        )

    return current_user
