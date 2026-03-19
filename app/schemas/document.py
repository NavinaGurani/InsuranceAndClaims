from pydantic import BaseModel
from datetime import datetime


class DocumentOut(BaseModel):
    id: int
    filename: str
    original_name: str
    content_type: str
    size_bytes: int
    claim_id: int | None
    uploader_id: int
    created_at: datetime

    model_config = {"from_attributes": True}
