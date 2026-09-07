from typing import Dict, Any, Optional
from .client import GitHubClient


class PullRequestService:
    def __init__(self, client: Optional[GitHubClient] = None):
        self.client = client or GitHubClient()

    def create_pull_request(
        self,
        owner: str,
        repo: str,
        title: str,
        head: str,
        base: str = "main",
        body: str = ""
    ) -> Dict[str, Any]:
        agent_footer = (
            "\n\n---\n*This PR was prepared by the local [GitHub AI Agent](https://github.com).* "
            "Merging must be performed manually by the repository maintainer."
        )
        payload = {
            "title": title,
            "head": head,
            "base": base,
            "body": body + agent_footer,
            "maintainer_can_modify": True,
        }
        return self.client.post(f"/repos/{owner}/{repo}/pulls", json_data=payload)
