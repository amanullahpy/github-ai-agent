import base64
import re
import hashlib
from typing import List, Dict, Any, Optional
from config import Config
from .client import GitHubClient

SECRET_PATTERNS = [
    re.compile(r"ghp_[0-9a-zA-Z]{36}"),                         # GitHub Personal Access Token
    re.compile(r"github_pat_[0-9a-zA-Z_]{82}"),                 # GitHub Fine-Grained PAT
    re.compile(r"AIza[0-9A-Za-z\\-_]{35}"),                     # Google API Key
    re.compile(r"sk-[a-zA-Z0-9]{20,48}"),                       # OpenAI API Key
    re.compile(r"-----BEGIN (RSA|EC|OPENSSH|DSA|PGP) PRIVATE KEY-----"), # Private Keys
    re.compile(r"(?i)(api[_-]?key|secret[_-]?token|password)\s*[:=]\s*['\"][^\n'\"]{8,}['\"]"),
]


class CommitService:
    def __init__(self, client: Optional[GitHubClient] = None):
        self.client = client or GitHubClient()

    @staticmethod
    def detect_secrets(content: str) -> List[str]:
        findings = []
        for pattern in SECRET_PATTERNS:
            matches = pattern.findall(content)
            if matches:
                findings.append(f"Potential secret detected matching pattern: {pattern.pattern[:30]}...")
        return findings

    @staticmethod
    def is_source_code_file(file_path: str) -> bool:
        protected_patterns = Config.get_protected_patterns()
        for pat in protected_patterns:
            ext = pat.replace("*", "")
            if file_path.endswith(ext):
                return True
        return False

    @staticmethod
    def is_allowed_file(file_path: str) -> bool:
        allowed = Config.get_allowed_fixable_patterns()
        normalized = file_path.replace("\\", "/")
        for pat in allowed:
            if pat.endswith("/**"):
                prefix = pat[:-3]
                if normalized.startswith(prefix):
                    return True
            elif normalized.lower() == pat.lower() or normalized.lower().endswith("/" + pat.lower()):
                return True
        return False

    def validate_change(self, file_path: str, new_content: str) -> None:
        # Defense-in-depth 1: Check if file is source code
        if self.is_source_code_file(file_path):
            raise PermissionError(
                f"SAFETY VIOLATION: Agent is strictly forbidden from modifying source code ({file_path})."
            )

        # Defense-in-depth 2: Check if file is in allowed fixable list
        if not self.is_allowed_file(file_path):
            raise PermissionError(
                f"SAFETY VIOLATION: Modifying {file_path} is not permitted under repository-level guidelines."
            )

        # Defense-in-depth 3: Secret scanning
        secrets = self.detect_secrets(new_content)
        if secrets:
            raise ValueError(f"SECRET SCANNING TRIGGERED: Proposed change contains potential secrets:\n" + "\n".join(secrets))

    def create_or_update_file(
        self,
        owner: str,
        repo: str,
        path: str,
        content: str,
        message: str,
        branch: str,
        sha: Optional[str] = None
    ) -> Dict[str, Any]:
        self.validate_change(path, content)

        if not sha:
            try:
                file_info = self.client.get(f"/repos/{owner}/{repo}/contents/{path}", params={"ref": branch})
                if isinstance(file_info, dict) and "sha" in file_info:
                    sha = file_info["sha"]
            except Exception:
                pass

        payload = {
            "message": f"chore(github-agent): {message}",
            "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
            "branch": branch,
        }
        if sha:
            payload["sha"] = sha

        return self.client.put(f"/repos/{owner}/{repo}/contents/{path}", json_data=payload)

