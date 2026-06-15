from fastapi import APIRouter, Depends,HTTPException
from app.middleware.webhook_auth import verify_webhook_signature
from app.models.schemas import WebhookPayload
from app.tasks.review_task import process_review

router = APIRouter()

@router.post("/api/webhook", status_code=202)
async def receive_webhook(body: bytes = Depends(verify_webhook_signature)):
    """接收 GitHub Webhook 请求，并将其发送到 Celery 任务队列进行处理"""
    import json
    payload = WebhookPayload(**json.loads(body))

    if payload.action not in ["opened", "synchronize"]:
      return {"message": f"Ignored action: {payload.action}"}
    if not payload.pull_request:
        raise HTTPException(400, "No pull request data found in the payload")
    # 将任务发送到 Celery 队列
    process_review.delay(
       repo_owner=payload.repository["owner"]["login"],
         repo_name=payload.repository["name"],
            pr_number=payload.pull_request["number"],
    )
    return {"message": "Review task queued","pr":payload.number}