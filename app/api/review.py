import time
import uuid
from fastapi import APIRouter
from pydantic import BaseModel
from app.agent.code_reviewer import review_code
from app.agent.security_scanner import scan_security
from app.agent.doc_reviewer import review_docs
from concurrent.futures import ThreadPoolExecutor

router = APIRouter()


class ReviewInput(BaseModel):
    code: str


class ReviewOutput(BaseModel):
    review_id: str
    code_review: str
    security_review: str
    doc_review: str
    issues_found: int
    duration: float


@router.post("/api/review", response_model=ReviewOutput)
async def review_endpoint(input: ReviewInput):
    """手动提交代码进行三 Agent 并行审查"""
    start = time.time()
    review_id = str(uuid.uuid4())

    with ThreadPoolExecutor(max_workers=3) as executor:
        f_code = executor.submit(review_code, input.code)
        f_security = executor.submit(scan_security, input.code)
        f_doc = executor.submit(review_docs, input.code)

    code_review = f_code.result()
    security_review = f_security.result()
    doc_review = f_doc.result()

    full = code_review + security_review + doc_review
    issues = full.count("[严重]") + full.count("[建议]") + full.count("[注入风险]")

    return ReviewOutput(
        review_id=review_id,
        code_review=code_review,
        security_review=security_review,
        doc_review=doc_review,
        issues_found=issues,
        duration=round(time.time() - start, 1),
    )
