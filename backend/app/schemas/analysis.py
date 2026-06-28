from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

class AnalysisResultResponse(BaseModel):
    id: UUID
    project_id: UUID
    file_path: str
    purpose: Optional[str] = None
    analysis: Optional[dict] = None
    dependencies: Optional[dict] = None
    connections: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True

class PromptResponse(BaseModel):
    id: UUID
    project_id: UUID
    prompt_text: str
    version: int
    metadata_: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True
