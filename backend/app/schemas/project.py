from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, HttpUrl

class ProjectBase(BaseModel):
    github_url: HttpUrl

class ProjectCreate(ProjectBase):
    gemini_api_key: Optional[str] = None

class ProjectResponse(ProjectBase):
    id: UUID
    name: str
    status: str
    technologies: Optional[dict] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ProjectListResponse(BaseModel):
    projects: List[ProjectResponse]
    total: int
