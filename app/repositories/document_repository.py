from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.document import Document
from app.repositories.base import BaseRepository


class DocumentRepository(BaseRepository[Document]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Document, session)

    async def list_by_claim(self, claim_id: int):
        result = await self.session.execute(select(Document).where(Document.claim_id == claim_id))
        return result.scalars().all()

    async def list_by_uploader(self, uploader_id: int, limit: int = 100, offset: int = 0):
        result = await self.session.execute(
            select(Document).where(Document.uploader_id == uploader_id).limit(limit).offset(offset)
        )
        return result.scalars().all()
