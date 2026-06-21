import uuid
from datetime import datetime
from app.models.schemas import ReviewRequest, ReviewResult
from app.services.knowledge_base import KnowledgeBase
from app.services.github import GitHubService
from app.agent.code_reviewer import review_code
 
class ReviewService:
    def __init__(self ,github_token:str):
        self.github = GitHubService(github_token)
        self.knowledge_base = KnowledgeBase()
    async def process_review(self, request:ReviewRequest)->ReviewResult:
        """执行完整的审查流程"""
        review_id = str(uuid.uuid4())

        #1.从知识库检索相关编码规范
        relevant_standards = self.knowledge_base.search(
            query=request.diff_content,
            top_k=3,
        )
        #2.把规范注入到审查上下文中
        context = ""
        if relevant_standards:
            context = "参考以下团队编码规范：\n" + "\n---\n".join(relevant_standards)

        # 3. 调用 Agent 执行审查（第 2 周：单 Agent；第 3 周：多 Agent 并行）
        review_report = review_code(request.diff_content)

        # 4. 组装最终评论
        comment_body = f"""## 🤖 CodeGuard 审查报告

{review_report}

{f"### 参考规范\n{context}" if context else ""}

---
*由 CodeGuard 自动生成 · Review ID: {review_id}*"""

        # 5. 发布评论到 GitHub PR
        await self.github.post_review_comment(
            owner=request.repo_owner,
            repo=request.repo_name,
            pr_number=request.pr_number,
            body=comment_body,
        )

        # 6. 返回审查结果
        return ReviewResult(
            review_id=review_id,
            pr_number=request.pr_number,
            status="completed",
            summary=review_report[:200],
            issues_found=review_report.count("[严重]") + review_report.count("[建议]"),
            created_at=datetime.now(),
        )