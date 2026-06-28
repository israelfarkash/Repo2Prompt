"""Project ORM model.

Represents a software repository submitted for analysis.
Tracks the project lifecycle from submission through analysis completion.
"""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.analysis import AnalysisResult
    from app.models.prompt import GeneratedPrompt


class Project(Base):
    """A software project submitted for reverse-engineering analysis.

    Attributes:
        id: Unique identifier (UUID v4).
        name: Human-readable project name, typically the repo name.
        github_url: Full URL of the GitHub repository.
        status: Current analysis status (pending, cloning, analyzing,
                generating, completed, failed).
        technologies: Detected technology stack as a JSON object.
        error_message: Error details if the analysis failed.
        created_at: Timestamp of project creation.
        updated_at: Timestamp of the last update.
        analysis_results: Related analysis results for individual files.
        generated_prompts: Generated mega-prompts for this project.
    """

    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    github_url: Mapped[str] = mapped_column(
        String(2048),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False,
    )
    technologies: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
        default=None,
    )
    error_message: Mapped[str | None] = mapped_column(
        String(2048),
        nullable=True,
        default=None,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=True,
        default=None,
    )

    analysis_results: Mapped[list["AnalysisResult"]] = relationship(
        "AnalysisResult",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    generated_prompts: Mapped[list["GeneratedPrompt"]] = relationship(
        "GeneratedPrompt",
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Project(id={self.id!r}, name={self.name!r}, status={self.status!r})>"
