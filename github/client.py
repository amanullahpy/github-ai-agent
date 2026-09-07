import time
import logging
from typing import Dict, Any, Optional
import requests
from config import Config

logger = logging.getLogger(__name__)


class GitHubClient:
    BASE_URL = "https://api.github.com"

    def __init__(self, token: Optional[str] = None):
        self.token = token or Config.GITHUB_TOKEN
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitHub-AI-Agent-Local/1.0",
        })
        if self.token:
            self.session.headers["Authorization"] = f"token {self.token}"

    def _check_rate_limit(self, response: requests.Response) -> None:
        remaining = response.headers.get("X-RateLimit-Remaining")
        reset_time = response.headers.get("X-RateLimit-Reset")
        if remaining is not None and int(remaining) <= 1:
            if reset_time:
                wait_seconds = max(1, int(reset_time) - int(time.time()))
                logger.warning(
                    f"GitHub API Rate limit almost exhausted. Remaining: {remaining}. Reset in {wait_seconds}s."
                )

    def request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        url = f"{self.BASE_URL}{endpoint}" if endpoint.startswith("/") else endpoint
        retries = 3
        backoff = 2

        for attempt in range(retries):
            try:
                response = self.session.request(method, url, timeout=20, **kwargs)
                self._check_rate_limit(response)

                if response.status_code == 403 and "rate limit exceeded" in response.text.lower():
                    reset_time = int(response.headers.get("X-RateLimit-Reset", time.time() + 60))
                    sleep_time = max(5, reset_time - int(time.time()))
                    logger.error(f"Rate limit exceeded. Waiting {sleep_time}s...")
                    time.sleep(min(sleep_time, 60))
                    continue

                if response.status_code == 404:
                    return {}

                if response.status_code >= 500:
                    time.sleep(backoff)
                    backoff *= 2
                    continue

                response.raise_for_status()
                if response.content:
                    return response.json()
                return {}

            except requests.exceptions.RequestException as e:
                logger.warning(f"Request error ({method} {endpoint}) on attempt {attempt+1}/{retries}: {e}")
                if attempt == retries - 1:
                    raise
                time.sleep(backoff)
                backoff *= 2

        return {}

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self.request("GET", endpoint, params=params)

    def post(self, endpoint: str, json_data: Optional[Dict[str, Any]] = None) -> Any:
        return self.request("POST", endpoint, json=json_data)

    def patch(self, endpoint: str, json_data: Optional[Dict[str, Any]] = None) -> Any:
        return self.request("PATCH", endpoint, json=json_data)

    def put(self, endpoint: str, json_data: Optional[Dict[str, Any]] = None) -> Any:
        return self.request("PUT", endpoint, json=json_data)
