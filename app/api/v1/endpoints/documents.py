from fastapi import APIRouter, Depends, UploadFile, File, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user_payload
from app.core.exceptions import NotFoundError, ForbiddenError
from app.db.session import get_session
from app.models.user import UserRole
from app.repositories.document_repository import DocumentRepository
from app.schemas.document import DocumentOut
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["Documents"])


def _svc(session: AsyncSession = Depends(get_session)) -> DocumentService:
    return DocumentService(session)


@router.post("/", response_model=DocumentOut, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    claim_id: int | None = Query(None),
    payload: dict = Depends(get_current_user_payload),
    svc: DocumentService = Depends(_svc),
):
    return await svc.upload(file, claim_id, int(payload["sub"]))


@router.get("/", response_model=list[DocumentOut])
async def list_documents(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    payload: dict = Depends(get_current_user_payload),
    svc: DocumentService = Depends(_svc),
):
    return await svc.list_documents(int(payload["sub"]), payload["role"], limit, offset)


@router.get("/{doc_id}", response_model=DocumentOut)
async def get_document_meta(
    doc_id: int,
    payload: dict = Depends(get_current_user_payload),
    svc: DocumentService = Depends(_svc),
):
    return await svc.get(doc_id, int(payload["sub"]), payload["role"])


@router.get("/{doc_id}/download")
async def download_document(
    doc_id: int,
    payload: dict = Depends(get_current_user_payload),
    session: AsyncSession = Depends(get_session),
):
    repo = DocumentRepository(session)
    doc = await repo.get(doc_id)
    if not doc:
        raise NotFoundError("Document not found")
    role = payload["role"]
    if role == UserRole.customer and doc.uploader_id != int(payload["sub"]):
        raise ForbiddenError()
    return FileResponse(doc.path, media_type=doc.content_type, filename=doc.original_name)
