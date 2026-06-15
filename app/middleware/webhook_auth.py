"""GitHub Webhook HMAC-SHA256 签名校验"""
import hmac
import hashlib
from fastapi import Request, HTTPException
from app.config import get_settings

settings = get_settings()


async def verify_webhook_signature(request: Request) -> bytes:
    """校验 GitHub Webhook 的 HMAC-SHA256 签名，防止伪造请求"""
    signature = request.headers.get("X-Hub-Signature-256", "")
    body = await request.body()

    expected_signature = (
        "sha256="
        + hmac.new(
            settings.github_webhook_secret.encode(),
            body,
            hashlib.sha256,
        ).hexdigest()
    )

    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    return body