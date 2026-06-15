from app.tasks.celery_app import celery_app

@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=10,  
    name="process_review",
)

def process_review(self, repo_owner: str, repo_name: str, pr_number: int):
    """异步执行代码审查"""
    try:
        #1.获取PRdiff
        #2.吊用Agent Pipeline
        #3.回写审查评论到GitHub
        pass
    except Exception as exc:
        #指数退避重试 10s->20s->40s
        raise self.retry(
            exc=exc,
            countdown=self.default_retry_delay * (2 ** self.request.retries)
        )