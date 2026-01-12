from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile

from app.repositories.attachment_repo import AttachmentRepository
from app.repositories.task_repo import TaskRepository
from app.db.models.attachment import Attachment
from app.core.exceptions import NotFoundError
from app.utils.file_storage import FileStorageService
from app.core.exceptions import AuthorizationError


class AttachmentService:
    def __init__(self):
        self.attachment_repo = AttachmentRepository()
        self.task_repo = TaskRepository()
        self.file_storage = FileStorageService()

    # ======================
    # Upload Attachment
    # ======================
    async def upload_attachment(
        self,
        db: AsyncSession,
        *,
        user,
        task_id,
        file: UploadFile,
    ) -> Attachment:
        # 1. Fetch task
        task = await self.task_repo.get_by_id(db, task_id)
        if not task or task.is_deleted:
            raise NotFoundError("Task not found")

        # 2. Authorization check
        validate_task_access(user, task)

        # 3. Store file on disk
        upload_result = await self.file_storage.upload_file(
        file=file,
        task_id=str(task.id),
        )

        # 4. Persist attachment record
        attachment = Attachment(
            task_id=task.id,
            uploaded_by_id=user.id,
            file_name=upload_result["original_filename"],
            file_path=upload_result["file_path"],   # relative path
            content_type=upload_result["content_type"],
            file_size=upload_result["file_size"],
        )

        return await self.attachment_repo.create(db, attachment)

    # ======================
    # List Attachments
    # ======================
    async def list_attachments_for_task(
        self,
        db: AsyncSession,
        *,
        user,
        task_id,
    ):
        task = await self.task_repo.get_by_id(db, task_id)
        if not task or task.is_deleted:
            raise NotFoundError("Task not found")

        validate_task_access(user, task)

        return await self.attachment_repo.get_by_task(db, task_id)

    # ======================
    # Download Attachment
    # ======================
    async def get_attachment_for_download(
        self,
        db: AsyncSession,
        *,
        user,
        attachment_id,
    ) -> Attachment:
        attachment = await self.attachment_repo.get_by_id(db, attachment_id)
        if not attachment:
            raise NotFoundError("Attachment not found")

        # IMPORTANT: auth via task, not attachment
        task = attachment.task
        if task.is_deleted:
            raise NotFoundError("Task not found")

        validate_task_access(user, task)

        return attachment



def validate_task_access(user, task):
    """
    Centralized RBAC check for task-level access.
    Used for attachment upload, list, and download.
    """

    # Admin: unrestricted
    if user.role == "ADMIN":
        return

    # Manager: same team only
    if user.role == "MANAGER":
        if task.team_id != user.team_id:
            raise AuthorizationError("Manager cannot access tasks outside their team")
        return

    # Member: only assigned tasks
    if user.role == "MEMBER":
        if task.assigned_to_id != user.id:
            raise AuthorizationError("Member can access only assigned tasks")
        return

    raise AuthorizationError("Invalid role")

