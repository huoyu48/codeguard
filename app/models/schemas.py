"""API 请求/响应模型"""
from pydantic import BaseModel, Field
from datetime import datetime


class WebhookPayload(BaseModel):
    """GitHub Webhook 载荷（简化版）"""
    action: str
    number: int | None = None
    repository: dict = Field(default_factory=dict)
    pull_request: dict | None = None


class ReviewRequest(BaseModel):
    """审查请求"""
    repo_owner: str
    repo_name: str
    pr_number: int
    diff_content: str
    language: str = "python"


class ReviewResult(BaseModel):
    """审查结果"""
    review_id: str
    pr_number: int
    status: str  # "pending" | "completed" | "failed"
    summary: str = ""
    issues_found: int = 0
    created_at: datetime = Field(default_factory=datetime.now)
