import sys
from typing import Dict, Any, Optional
from database import Database, get_db


class ApprovalManager:
    def __init__(self, db: Optional[Database] = None):
        self.db = db or get_db()

    def prompt_user(self, solution: Dict[str, Any], repo_name: str, auto_approve: bool = False) -> str:
        """
        Returns 'APPROVE', 'REJECT', or 'SKIP'
        """
        if auto_approve:
            self._record_decision(solution["id"], "APPROVE", "Auto-approved via flags")
            return "APPROVE"

        border = "=" * 40
        print(f"\n{border}")
        print("GITHUB AGENT — APPROVAL REQUIRED")
        print(f"{border}")
        print(f"Repository:      {repo_name}")
        print(f"Issue:           {solution.get('title')}")
        print(f"Files Affected:  {solution.get('target_file')}")
        print(f"Risk Level:      {solution.get('risk_level', 'LOW')}")
        print(f"Proposed change: {solution.get('proposed_change', '')[:100]}...")
        print(f"{border}")

        while True:
            choice = input("[Y] Approve  [N] Reject  [V] View diff  [S] Skip : ").strip().upper()
            if choice == "Y":
                self._record_decision(solution["id"], "APPROVE")
                return "APPROVE"
            elif choice == "N":
                self._record_decision(solution["id"], "REJECT")
                return "REJECT"
            elif choice == "S":
                self._record_decision(solution["id"], "SKIP")
                return "SKIP"
            elif choice == "V":
                print("\n--- UNIFIED DIFF ---")
                print(solution.get("diff", "No diff available."))
                print("--------------------\n")
            else:
                print("Invalid option. Please choose Y, N, V, or S.")

    def _record_decision(self, solution_id: int, action: str, notes: str = "") -> None:
        with self.db.get_connection() as conn:
            conn.execute(
                "INSERT INTO approvals (solution_id, action, notes) VALUES (?, ?, ?)",
                (solution_id, action, notes)
            )
            new_status = "APPROVED" if action == "APPROVE" else ("REJECTED" if action == "REJECT" else "PENDING")
            conn.execute(
                "UPDATE solutions SET status = ? WHERE id = ?",
                (new_status, solution_id)
            )
            conn.commit()
