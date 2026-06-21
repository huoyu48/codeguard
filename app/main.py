"""CodeGuard - AI 代码审查自动化平台"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.api.webhook import router as webhook_router
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


@app.get("/health")
async def health_check():
    return {"status": "ok", "app": "CodeGuard", "version": "0.1.0"}
