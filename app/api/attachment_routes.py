from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.services.attachment_service import AttachmentService


router = APIRouter(tags=["Attachments"])
attachment_service = AttachmentService()

@router.post("/tasks/{task_id}/attachments")
async def upload_attachment(
    task_id,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await attachment_service.upload_attachment(
        db,
        user=current_user,
        task_id=task_id,
        file=file,
    )

@router.get("/tasks/{task_id}/attachments")
async def list_attachments(
    task_id,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await attachment_service.list_attachments_for_task(
        db,
        user=current_user,
        task_id=task_id,
    )


@router.get("/attachments/{attachment_id}")
async def download_attachment(
    attachment_id,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    attachment = await attachment_service.get_attachment_for_download(
        db,
        user=current_user,
        attachment_id=attachment_id,
    )

    full_path = attachment_service.file_storage.base_path / attachment.file_path

    return FileResponse(
        path=full_path,
        media_type=attachment.content_type,
        filename=attachment.file_name,
    )


