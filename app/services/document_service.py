import uuid
import os
import aiofiles
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import NotFoundError, ForbiddenError, BadRequestError
from app.models.document import Document
from app.models.user import UserRole
from app.repositories.document_repository import DocumentRepository
from app.repositories.claim_repository import ClaimRepository
from app.schemas.document import DocumentOut

ALLOWED_TYPES = {"application/pdf", "image/jpeg", "image/png", "image/webp"}


class DocumentService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = DocumentRepository(session)
        self.claim_repo = ClaimRepository(session)

    async def upload(self, file: UploadFile, claim_id: int | None, uploader_id: int) -> DocumentOut:
        if file.content_type not in ALLOWED_TYPES:
            raise BadRequestError(f"File type {file.content_type} not allowed")

        content = await file.read()
        max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
        if len(content) > max_bytes:
            raise BadRequestError(f"File exceeds {settings.MAX_FILE_SIZE_MB}MB limit")

        if claim_id:
            claim = await self.claim_repo.get(claim_id)
            if not claim:
                raise NotFoundError("Claim not found")

        ext = os.path.splitext(file.filename or "file")[1]
        unique_name = f"{uuid.uuid4().hex}{ext}"
        path = os.path.join(settings.UPLOAD_DIR, unique_name)
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

        async with aiofiles.open(path, "wb") as f:
            await f.write(content)

        doc = Document(
            filename=unique_name,
            original_name=file.filename or unique_name,
            content_type=file.content_type,
            size_bytes=len(content),
            path=path,
            claim_id=claim_id,
            uploader_id=uploader_id,
        )
        created = await self.repo.create(doc)
        return DocumentOut.model_validate(created)

    async def get(self, doc_id: int, user_id: int, role: str) -> DocumentOut:
        doc = await self.repo.get(doc_id)
        if not doc:
            raise NotFoundError("Document not found")
        if role == UserRole.customer and doc.uploader_id != user_id:
            raise ForbiddenError()
        return DocumentOut.model_validate(doc)

    async def list_documents(self, user_id: int, role: str, limit: int, offset: int):
        if role in (UserRole.admin, UserRole.agent):
            docs = await self.repo.list(limit=limit, offset=offset)
        else:
            docs = await self.repo.list_by_uploader(user_id, limit=limit, offset=offset)
        return [DocumentOut.model_validate(d) for d in docs]
