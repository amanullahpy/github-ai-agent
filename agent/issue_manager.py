import hashlib
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from database import Database, get_db
from database.models import RepositoryIssue
from .classifier import IssueClassifier


class IssueManager:
    def __init__(self, db: Optional[Database] = None):
        self.db = db or get_db()

    @staticmethod
    def compute_issue_hash(repo_full_name: str, issue_type: str, description: str, resource: str) -> str:
        norm_desc = " ".join(description.strip().lower().split())
        norm_res = resource.strip().replace("\\", "/").lower()
        payload = f"{repo_full_name}:{issue_type}:{norm_desc}:{norm_res}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def record_issue(
        self,
        repository_id: int,
        repo_full_name: str,
        issue_type: str,
        description: str,
        affected_resource: str,
        severity: str = "LOW"
    ) -> RepositoryIssue:
        category, status = IssueClassifier.classify(issue_type, affected_resource)
        issue_hash = self.compute_issue_hash(repo_full_name, issue_type, description, affected_resource)

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, status FROM repository_issues WHERE issue_hash = ?", (issue_hash,))
            row = cursor.fetchone()

            if row:
                # Update last_seen_at without overwriting user state
                issue_id = row["id"]
                now_iso = datetime.now(timezone.utc).isoformat()
                cursor.execute(
                    "UPDATE repository_issues SET last_seen_at = ?, severity = ? WHERE id = ?",
                    (now_iso, severity, issue_id)
                )

                conn.commit()
                return RepositoryIssue(
                    id=issue_id,
                    repository_id=repository_id,
                    category=category,
                    issue_type=issue_type,
                    description=description,
                    affected_resource=affected_resource,
                    severity=severity,
                    status=row["status"],
                    issue_hash=issue_hash,
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO repository_issues
                    (repository_id, category, issue_type, description, affected_resource, severity, status, issue_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (repository_id, category, issue_type, description, affected_resource, severity, status, issue_hash)
                )
                conn.commit()
                return RepositoryIssue(
                    id=cursor.lastrowid,
                    repository_id=repository_id,
                    category=category,
                    issue_type=issue_type,
                    description=description,
                    affected_resource=affected_resource,
                    severity=severity,
                    status=status,
                    issue_hash=issue_hash,
                )

    def list_issues(self, repository_id: Optional[int] = None) -> List[Dict[str, Any]]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            if repository_id:
                cursor.execute("SELECT * FROM repository_issues WHERE repository_id = ? ORDER BY id DESC", (repository_id,))
            else:
                cursor.execute("SELECT * FROM repository_issues ORDER BY id DESC")
            return [dict(r) for r in cursor.fetchall()]
