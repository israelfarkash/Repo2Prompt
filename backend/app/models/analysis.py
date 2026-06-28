import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, JSON, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.project import Project

class AnalysisResult(Base):
    """Analysis result for a specific file or component in a project."""

    __tablename__ = "analysis_results"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    file_path: Mapped[str] = mapped_column(String(2048), nullable=False)
    purpose: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    analysis: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=None)
    dependencies: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=None)
    connections: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    project: Mapped["Project"] = relationship("Project", back_populates="analysis_results")

    def __repr__(self) -> str:
        return f"<AnalysisResult(id={self.id!r}, project_id={self.project_id!r}, file_path={self.file_path!r})>"
