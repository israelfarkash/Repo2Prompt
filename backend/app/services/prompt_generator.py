import json
import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.project import Project
from app.models.analysis import AnalysisResult
from app.models.prompt import GeneratedPrompt
from app.ai.base_provider import AIProvider

logger = logging.getLogger(__name__)

async def generate_mega_prompt(project_id: UUID, db: AsyncSession, provider: AIProvider) -> None:
    """Generate the final mega prompt from collected analysis results."""
    
    # Get project info
    stmt = select(Project).where(Project.id == project_id)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    
    if not project:
        raise ValueError(f"Project {project_id} not found")
        
    # Get analysis results
    stmt = select(AnalysisResult).where(AnalysisResult.project_id == project_id)
    result = await db.execute(stmt)
    analyses_records = result.scalars().all()
    
    analyses_list = []
    for record in analyses_records:
        analyses_list.append({
            "file_path": record.file_path,
            "purpose": record.purpose,
            "analysis": record.analysis
        })
        
    project_info = {
        "name": project.name,
        "github_url": project.github_url,
        "technologies": project.technologies
    }
    
    logger.info(f"Generating mega prompt for project {project_id} using {provider.get_model_name()}")
    
    # Generate the prompt text using the AI provider
    # The provider handles ensuring the output is in English
    prompt_text = await provider.generate_synthesis(analyses_list, project_info)
    
    # Save to database
    prompt = GeneratedPrompt(
        project_id=project_id,
        prompt_text=prompt_text,
        version=1,
        metadata_={"model": provider.get_model_name()}
    )
    
    db.add(prompt)
    await db.commit()
    logger.info(f"Successfully generated mega prompt for project {project_id}")
