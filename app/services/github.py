import httpx
from app.config import get_settings

settings = get_settings()

class GitHubService:
    BASE_URL = "https://api.github.com"

    def __init__(self, access_token: str):
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"token {access_token}",
                "Accept": "application/vnd.github.v3+json",
            },
            timeout=30,
        )
    async def get_pr_diff(self,owner: str, repo: str, pr_number: int) -> str:
        resp = await self.client.get(f"{self.BASE_URL}/repos/{owner}/{repo}/pulls/{pr_number}", headers={"Accept": "application/vnd.github.v3.diff"})
        resp.raise_for_status()
        return resp.text
    async def post_review_comment(self,owner: str, repo: str, pr_number: int, body: str)-> dict:
        resp = await self.client.post(
            f"{self.BASE_URL}/repos/{owner}/{repo}/issues/{pr_number}/comments",
            json={"body": body},
        )
        resp.raise_for_status()
        return resp.json()