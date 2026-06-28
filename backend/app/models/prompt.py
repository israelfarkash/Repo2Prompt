import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, JSON, DateTime, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.project import Project

class GeneratedPrompt(Base):
    """A generated mega-prompt based on project analysis."""

    __tablename__ = "generated_prompts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    prompt_text: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    project: Mapped["Project"] = relationship("Project", back_populates="generated_prompts")

    def __repr__(self) -> str:
        return f"<GeneratedPrompt(id={self.id!r}, project_id={self.project_id!r}, version={self.version!r})>"
