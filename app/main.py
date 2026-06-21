"""CodeGuard - AI 代码审查自动化平台"""
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from app.config import get_settings
from app.api.webhook import router as webhook_router
from app.api.review import router as review_router
from dotenv import load_dotenv

load_dotenv()
settings = get_settings()

app = FastAPI(
    title="CodeGuard API",
    description="AI-powered code review automation platform",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhook_router)
app.include_router(review_router)


@app.get("/")
async def index():
    """Web UI 入口"""
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.get("/health")
async def health_check():
    return {"status": "ok", "app": "CodeGuard", "version": "0.1.0"}
