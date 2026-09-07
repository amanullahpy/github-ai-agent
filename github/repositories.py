import base64
from typing import List, Dict, Any, Optional
from .client import GitHubClient


class RepositoryService:
    def __init__(self, client: Optional[GitHubClient] = None):
        self.client = client or GitHubClient()

    def get_user_profile(self, username: Optional[str] = None) -> Dict[str, Any]:
        endpoint = f"/users/{username}" if username else "/user"
        return self.client.get(endpoint)

    def list_repositories(self, username: Optional[str] = None) -> List[Dict[str, Any]]:
        # If token is configured, determine if username is the authenticated user
        is_authenticated_user = False
        if self.client.token:
            if not username:
                is_authenticated_user = True
            else:
                try:
                    auth_profile = self.client.get("/user")
                    if auth_profile.get("login", "").lower() == username.lower():
                        is_authenticated_user = True
                except Exception:
                    pass

        all_repos: List[Dict[str, Any]] = []
        page = 1

        while True:
            if is_authenticated_user:
                endpoint = "/user/repos"
                params = {
                    "per_page": 100,
                    "sort": "updated",
                    "visibility": "all",
                    "affiliation": "owner,collaborator,organization_member",
                    "page": page,
                }
            else:
                endpoint = f"/users/{username}/repos"
                params = {
                    "per_page": 100,
                    "sort": "updated",
                    "page": page,
                }

            page_data = self.client.get(endpoint, params=params)
            if not isinstance(page_data, list) or len(page_data) == 0:
                break

            all_repos.extend(page_data)
            if len(page_data) < 100:
                break
            page += 1

        return all_repos


    def get_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        return self.client.get(f"/repos/{owner}/{repo}")

    def get_file_content(self, owner: str, repo: str, path: str, ref: Optional[str] = None) -> Optional[str]:
        params = {"ref": ref} if ref else None
        try:
            data = self.client.get(f"/repos/{owner}/{repo}/contents/{path}", params=params)
            if isinstance(data, dict) and data.get("encoding") == "base64" and "content" in data:
                return base64.b64decode(data["content"]).decode("utf-8", errors="replace")
        except Exception:
            return None
        return None

    def get_directory_contents(self, owner: str, repo: str, path: str = "") -> List[Dict[str, Any]]:
        try:
            data = self.client.get(f"/repos/{owner}/{repo}/contents/{path}")
            return data if isinstance(data, list) else []
        except Exception:
            return []
