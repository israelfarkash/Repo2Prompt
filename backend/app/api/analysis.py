from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.project import Project
from app.models.analysis import AnalysisResult
from app.models.prompt import GeneratedPrompt
from app.schemas.analysis import AnalysisResultResponse, PromptResponse

router = APIRouter(prefix="/projects/{project_id}", tags=["analysis"])

@router.get("/analysis", response_model=List[AnalysisResultResponse])
async def get_project_analysis(project_id: UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(AnalysisResult).where(AnalysisResult.project_id == project_id)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/prompt", response_model=PromptResponse)
async def get_project_prompt(project_id: UUID, db: AsyncSession = Depends(get_db)):
    # Get the latest prompt version
    stmt = select(GeneratedPrompt).where(GeneratedPrompt.project_id == project_id).order_by(GeneratedPrompt.version.desc())
    result = await db.execute(stmt)
    prompt = result.scalars().first()
    
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not generated yet")
        
    return prompt

@router.post("/regenerate", response_model=PromptResponse)
async def regenerate_prompt(
    project_id: UUID, 
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Project).where(Project.id == project_id)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    if project.status != "completed":
        raise HTTPException(status_code=400, detail="Cannot regenerate before analysis is complete")
        
    project.status = "generating"
    await db.commit()
    
    from app.services.analyzer_service import update_progress
    update_progress(project_id, "generating", "Regenerating Master Prompt", 0)
    
    # Run in background
    background_tasks.add_task(run_regeneration, project_id)
    
    return {"status": "started"}
    
async def run_regeneration(project_id: UUID):
    from app.database import AsyncSessionLocal
    from app.services.prompt_generator import generate_mega_prompt
    from app.ai.factory import get_ai_provider
    from app.config import settings
    from app.services.analyzer_service import update_progress
    
    try:
        async with AsyncSessionLocal() as db:
            stmt = select(Project).where(Project.id == project_id)
            result = await db.execute(stmt)
            project = result.scalar_one_or_none()
            
            provider = get_ai_provider(
                provider_name=settings.AI_PROVIDER,
                api_key=settings.GEMINI_API_KEY,
                model=settings.AI_MODEL
            )
            
            await generate_mega_prompt(project_id, db, provider)
            
            project.status = "completed"
            await db.commit()
            update_progress(project_id, "completed", "Done", 100)
    except Exception as e:
        async with AsyncSessionLocal() as db:
            stmt = select(Project).where(Project.id == project_id)
            result = await db.execute(stmt)
            project = result.scalar_one_or_none()
            if project:
                project.status = "failed"
                project.error_message = str(e)
                await db.commit()
                update_progress(project_id, "failed", f"Error: {str(e)}", 0)
