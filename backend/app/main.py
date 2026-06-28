from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import async_engine, Base
from app.api import projects, analysis

@asynccontextmanager
async def lifespan(app: FastAPI):
    # For MVP, create tables on startup if they don't exist
    # In production, we use alembic migrations
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await async_engine.dispose()

app = FastAPI(
    title="AI Project Reverse Engineer API",
    description="Deep project analysis and mega-prompt generation",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "ai-project-reverse-engineer"}
