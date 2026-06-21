import asyncio
from app.tasks.celery_app import celery_app
from app.config import get_settings
from app.services.github import GitHubService
from app.services.review_service import ReviewService
from app.models.schemas import ReviewRequest

settings = get_settings()


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=10,
    name="process_review",
)
def process_review(self, repo_owner: str, repo_name: str, pr_number: int):
    """异步执行代码审查"""
    try:
        # 1. 获取 PR diff
        github = GitHubService(settings.github_token)
        diff_content = asyncio.run(
            github.get_pr_diff(repo_owner, repo_name, pr_number)
        )

        # 2. 调用 Agent Pipeline（三 Agent 并行 + RAG）
        service = ReviewService(settings.github_token)
        request = ReviewRequest(
            repo_owner=repo_owner,
            repo_name=repo_name,
            pr_number=pr_number,
            diff_content=diff_content,
        )

        # 3. ReviewService 内部已完成回写审查评论到 GitHub
        asyncio.run(service.process_review(request))

    except Exception as exc:
        # 指数退避重试 10s->20s->40s
        raise self.retry(
            exc=exc,
            countdown=self.default_retry_delay * (2 ** self.request.retries)
        )