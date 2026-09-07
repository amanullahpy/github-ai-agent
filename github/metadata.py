from typing import List, Dict, Any, Optional
from .client import GitHubClient


class MetadataService:
    def __init__(self, client: Optional[GitHubClient] = None):
        self.client = client or GitHubClient()

    def update_repository_metadata(
        self,
        owner: str,
        repo: str,
        description: Optional[str] = None,
        homepage: Optional[str] = None,
        has_issues: Optional[bool] = None,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {}
        if description is not None:
            payload["description"] = description
        if homepage is not None:
            payload["homepage"] = homepage
        if has_issues is not None:
            payload["has_issues"] = has_issues

        if not payload:
            return {}
        return self.client.patch(f"/repos/{owner}/{repo}", json_data=payload)

    def update_topics(self, owner: str, repo: str, topics: List[str]) -> Dict[str, Any]:
        return self.client.put(
            f"/repos/{owner}/{repo}/topics",
            json_data={"names": [t.lower().strip() for t in topics if t.strip()]}
        )
