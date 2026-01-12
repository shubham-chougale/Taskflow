from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.db.models.attachment import Attachment


class AttachmentRepository:
    async def create( self, db: AsyncSession, attachment: Attachment ) -> Attachment:
        db.add(attachment)
        await db.commit()
        await db.refresh(attachment)
        return attachment

    async def get_by_id(self, db, attachment_id):
        stmt = (
            select(Attachment)
            .where(Attachment.id == attachment_id)
            .options(
                selectinload(Attachment.task),
                selectinload(Attachment.uploaded_by),
            )
        )

        result = await db.execute(stmt)
        return result.scalar_one_or_none()


    async def get_by_task( self, db: AsyncSession, task_id ) -> list[Attachment]:
        result = await db.execute(
            select(Attachment)
            .where(Attachment.task_id == task_id)
            .order_by(Attachment.created_at.desc())
        )
        return result.scalars().all()
