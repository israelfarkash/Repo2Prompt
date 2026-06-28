import asyncio
from typing import List
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.database import get_db, AsyncSessionLocal
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectListResponse
from app.services.github_service import extract_repo_info, clone_repository, cleanup_repository
from app.services.analyzer_service import run_full_analysis, progress_store

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("", response_model=ProjectResponse)
async def create_project(
    project_in: ProjectCreate, 
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    url = str(project_in.github_url)
    
    # Extract name
    info = await extract_repo_info(url)
    project_name = f"{info['owner']}/{info['name']}"
    
    # Create DB record
    project = Project(
        name=project_name,
        github_url=url,
        status="pending"
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    
    # Start background task
    background_tasks.add_task(process_project_background, project.id, url, project_in.gemini_api_key)
    
    return project

async def process_project_background(project_id: UUID, url: str, api_key: str = None):
    # This needs a fresh DB session since it runs in background
    async_session_maker = AsyncSessionLocal
    
    repo_path = None
    try:
        async with AsyncSessionLocal() as db:
            # Clone
            from app.services.analyzer_service import update_progress
            update_progress(project_id, "cloning", "Cloning Repository", 5)
            
            repo_path = await clone_repository(url, project_id)
            
            # Analyze
            await run_full_analysis(project_id, repo_path, db, api_key)
            
    except Exception as e:
        async with AsyncSessionLocal() as db:
            stmt = select(Project).where(Project.id == project_id)
            result = await db.execute(stmt)
            project = result.scalar_one_or_none()
            if project:
                project.status = "failed"
                project.error_message = str(e)
                await db.commit()
    finally:
        if repo_path:
            await cleanup_repository(repo_path)

@router.get("", response_model=ProjectListResponse)
async def list_projects(db: AsyncSession = Depends(get_db)):
    stmt = select(Project).order_by(Project.created_at.desc())
    result = await db.execute(stmt)
    projects = result.scalars().all()
    return {"projects": projects, "total": len(projects)}

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(Project).where(Project.id == project_id)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    return project

@router.delete("/{project_id}")
async def delete_project_endpoint(project_id: UUID, db: AsyncSession = Depends(get_db)):
    stmt = select(Project).where(Project.id == project_id)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    await db.delete(project)
    await db.commit()
    
    # Cleanup memory
    pid = str(project_id)
    if pid in progress_store:
        del progress_store[pid]
        
    return {"status": "success"}

import json
from sse_starlette.sse import EventSourceResponse
from fastapi import Request

@router.get("/{project_id}/status")
async def project_status_stream(request: Request, project_id: UUID, db: AsyncSession = Depends(get_db)):
    """SSE endpoint for real-time progress."""
    
    # Check if exists
    stmt = select(Project).where(Project.id == project_id)
    result = await db.execute(stmt)
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    async def event_generator():
        pid = str(project_id)
        last_status = None
        
        while True:
            if await request.is_disconnected():
                break
                
            # Check db status if not in progress_store
            current_progress = progress_store.get(pid)
            
            if not current_progress:
                # Fallback to DB
                async with AsyncSessionLocal() as session:
                    stmt = select(Project.status).where(Project.id == project_id)
                    res = await session.execute(stmt)
                    status = res.scalar_one_or_none()
                    if status:
                        current_progress = {"status": status, "stage": status.capitalize(), "progress": 0}
                        if status == "completed": current_progress["progress"] = 100
                        if status == "failed": current_progress["progress"] = 0

            if current_progress and current_progress != last_status:
                yield {
                    "data": json.dumps(current_progress)
                }
                last_status = current_progress.copy()
                
                if current_progress.get("status") in ("completed", "failed"):
                    break
                    
            await asyncio.sleep(1)

    return EventSourceResponse(event_generator())
