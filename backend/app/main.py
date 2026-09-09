"""
ResumeIQ - FastAPI Application.

Application entry point for the ResumeIQ backend.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.resume_library import router as resume_library_router
from app.api.routes import router as resume_router
from app.db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize application resources during startup."""

    init_db()

    yield


app = FastAPI(
    title="ResumeIQ API",
    description="AI Powered Resume Analysis Platform",
    version="1.0.0",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(resume_router)
app.include_router(resume_library_router)


@app.get("/")
def root():
    return {
        "message": "ResumeIQ backend is running",
        "version": "1.0.0",
    }