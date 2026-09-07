import hashlib
import difflib
from datetime import datetime
from typing import Optional, List, Dict, Any
from database import Database, get_db
from database.models import Solution, SolutionChange
from github.commits import CommitService


class SolutionManager:
    PROMPT_VERSION = "1.0"

    def __init__(self, db: Optional[Database] = None):
        self.db = db or get_db()

    @classmethod
    def compute_solution_hash(cls, issue_hash: str, proposed_change: str) -> str:
        norm_change = " ".join(proposed_change.strip().split())
        payload = f"{issue_hash}:{norm_change}:{cls.PROMPT_VERSION}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @staticmethod
    def generate_unified_diff(original_content: str, new_content: str, filename: str) -> str:
        diff_lines = difflib.unified_diff(
            original_content.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile=f"a/{filename}",
            tofile=f"b/{filename}",
        )
        return "".join(diff_lines)

    def create_solution(
        self,
        issue_id: int,
        repository_id: int,
        issue_hash: str,
        title: str,
        target_file: str,
        original_content: str,
        new_content: str,
        risk_level: str = "LOW"
    ) -> Solution:
        # Multi-layer safety: Never permit source code modification
        if CommitService.is_source_code_file(target_file):
            raise PermissionError(f"Safety Violation: Cannot create solution for source-code file {target_file}")

        if not CommitService.is_allowed_file(target_file):
            raise PermissionError(f"Safety Violation: Target file {target_file} is not in allowed fixable list")

        diff = self.generate_unified_diff(original_content, new_content, target_file)
        solution_hash = self.compute_solution_hash(issue_hash, new_content)

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, status FROM solutions WHERE solution_hash = ?", (solution_hash,))
            row = cursor.fetchone()

            if row:
                # Existing solution reused
                return Solution(
                    id=row["id"],
                    issue_id=issue_id,
                    repository_id=repository_id,
                    title=title,
                    proposed_change=new_content,
                    target_file=target_file,
                    diff=diff,
                    risk_level=risk_level,
                    solution_hash=solution_hash,
                    status=row["status"],
                )

            cursor.execute(
                """
                INSERT INTO solutions
                (issue_id, repository_id, title, proposed_change, target_file, diff, risk_level, solution_hash, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'PENDING')
                """,
                (issue_id, repository_id, title, new_content, target_file, diff, risk_level, solution_hash)
            )
            sol_id = cursor.lastrowid

            cursor.execute(
                """
                INSERT INTO solution_changes
                (solution_id, file_path, change_type, before_hash, after_hash, diff, approved, applied)
                VALUES (?, ?, 'UPDATE', ?, ?, ?, 0, 0)
                """,
                (
                    sol_id,
                    target_file,
                    hashlib.sha256(original_content.encode("utf-8")).hexdigest(),
                    hashlib.sha256(new_content.encode("utf-8")).hexdigest(),
                    diff,
                )
            )
            conn.commit()

            return Solution(
                id=sol_id,
                issue_id=issue_id,
                repository_id=repository_id,
                title=title,
                proposed_change=new_content,
                target_file=target_file,
                diff=diff,
                risk_level=risk_level,
                solution_hash=solution_hash,
                status="PENDING",
            )

    def list_solutions(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            if status:
                cursor.execute("SELECT * FROM solutions WHERE status = ? ORDER BY id DESC", (status.upper(),))
            else:
                cursor.execute("SELECT * FROM solutions ORDER BY id DESC")
            return [dict(r) for r in cursor.fetchall()]
