import asyncio
import logging
from typing import Dict, Any, Callable
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.project import Project
from app.models.analysis import AnalysisResult
from app.services.scanner_service import scan_project
from app.ai.factory import get_ai_provider
from app.config import settings

logger = logging.getLogger(__name__)

# Simple in-memory store for MVP SSE progress tracking
# Format: {project_id_str: {"status": "analyzing", "stage": "Stage Name", "progress": 50}}
progress_store: Dict[str, Dict[str, Any]] = {}

def update_progress(project_id: UUID, status: str, stage: str, progress: int):
    """Update progress store for SSE."""
    pid = str(project_id)
    if pid not in progress_store:
        progress_store[pid] = {}
    progress_store[pid] = {
        "status": status,
        "stage": stage,
        "progress": progress
    }
    logger.info(f"Project {pid} progress: {status} - {stage} ({progress}%)")

async def run_full_analysis(project_id: UUID, repo_path: str, db: AsyncSession, api_key: str = None):
    """Run the complete analysis pipeline."""
    try:
        # Fetch project
        stmt = select(Project).where(Project.id == project_id)
        result = await db.execute(stmt)
        project = result.scalar_one_or_none()
        
        if not project:
            logger.error(f"Project {project_id} not found")
            return

        provider = get_ai_provider(
            provider_name=settings.AI_PROVIDER,
            api_key=api_key or settings.GEMINI_API_KEY,
            model=settings.AI_MODEL
        )

        # 1. Scanning
        update_progress(project_id, "scanning", "Scanning Files", 10)
        project.status = "scanning"
        await db.commit()
        
        scan_data = await scan_project(repo_path)
        project.technologies = scan_data["technologies"]
        await db.commit()

        # 2. Analysis
        update_progress(project_id, "analyzing", "Understanding Architecture", 30)
        project.status = "analyzing"
        await db.commit()

        # Here we would chunk files and send to AI.
        # For MVP, we do a basic structural analysis.
        arch_analysis = await provider.analyze_architecture(
            structure=scan_data["file_tree"],
            tech_stack=scan_data["technologies"]
        )

        # Save to DB
        arch_result = AnalysisResult(
            project_id=project_id,
            file_path="[ARCHITECTURE]",
            purpose="Overall architecture analysis",
            analysis=arch_analysis
        )
        db.add(arch_result)
        await db.commit()
        
        update_progress(project_id, "analyzing", "Sending Analysis To AI", 60)
        
        # In a full implementation, we'd loop over important files and analyze them.
        
        # 3. Prompt Generation
        update_progress(project_id, "generating", "Generating Master Prompt", 85)
        project.status = "generating"
        await db.commit()
        
        from app.services.prompt_generator import generate_mega_prompt
        await generate_mega_prompt(project_id, db, provider)
        
        # 4. Done
        project.status = "completed"
        await db.commit()
        update_progress(project_id, "completed", "Done", 100)
        
    except Exception as e:
        logger.exception(f"Analysis failed for project {project_id}")
        project.status = "failed"
        project.error_message = str(e)
        await db.commit()
        update_progress(project_id, "failed", f"Error: {str(e)}", 0)
