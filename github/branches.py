import logging
from typing import Dict, Any, Optional
from .client import GitHubClient

logger = logging.getLogger(__name__)


class BranchService:
    def __init__(self, client: Optional[GitHubClient] = None):
        self.client = client or GitHubClient()

    def get_branch_sha(self, owner: str, repo: str, branch: str = "main") -> Optional[str]:
        try:
            ref_data = self.client.get(f"/repos/{owner}/{repo}/git/ref/heads/{branch}")
            if isinstance(ref_data, dict) and "object" in ref_data:
                return ref_data["object"]["sha"]
        except Exception as e:
            logger.error(f"Error fetching branch {branch} for {owner}/{repo}: {e}")
        return None

    def create_safe_branch(
        self,
        owner: str,
        repo: str,
        branch_name: str,
        base_branch: str = "main"
    ) -> Dict[str, Any]:
        if not branch_name.startswith("github-agent/"):
            branch_name = f"github-agent/{branch_name}"

        base_sha = self.get_branch_sha(owner, repo, base_branch)
        if not base_sha and base_branch != "master":
            base_sha = self.get_branch_sha(owner, repo, "master")
        if not base_sha:
            raise ValueError(f"Could not determine base branch SHA for {base_branch} or master")

        payload = {
            "ref": f"refs/heads/{branch_name}",
            "sha": base_sha,
        }
        try:
            return self.client.post(f"/repos/{owner}/{repo}/git/refs", json_data=payload)
        except Exception as e:
            # If branch already exists, retrieve existing ref
            logger.info(f"Branch {branch_name} may already exist: {e}")
            existing = self.client.get(f"/repos/{owner}/{repo}/git/ref/heads/{branch_name}")
            if existing:
                return existing
            raise

