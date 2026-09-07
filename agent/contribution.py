from typing import List, Dict, Any, Optional
from database import Database, get_db
from database.models import Contribution


class ContributionManager:
    def __init__(self, db: Optional[Database] = None):
        self.db = db or get_db()

    def identify_opportunities(self, repository_id: int, repo_name: str) -> List[Dict[str, Any]]:
        opportunities = []
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT issue_type, description, affected_resource, severity
                FROM repository_issues
                WHERE repository_id = ? AND status = 'FIXABLE'
                """,
                (repository_id,)
            )
            issues = cursor.fetchall()

            for issue in issues:
                itype = issue["issue_type"]
                desc = issue["description"]
                if itype == "MISSING_README_INSTALLATION":
                    opportunities.append({
                        "repository": repo_name,
                        "type": "README_SETUP",
                        "description": "Improve README setup and installation documentation.",
                        "why": desc,
                        "difficulty": "Low",
                        "estimated_minutes": 15,
                        "agent_can_prepare": "README update",
                        "requires_approval": True,
                    })
                elif itype == "MISSING_README_USAGE":
                    opportunities.append({
                        "repository": repo_name,
                        "type": "README_USAGE",
                        "description": "Add clear usage instructions and code snippets.",
                        "why": desc,
                        "difficulty": "Low",
                        "estimated_minutes": 15,
                        "agent_can_prepare": "README update",
                        "requires_approval": True,
                    })
                elif itype == "MISSING_PR_TEMPLATE":
                    opportunities.append({
                        "repository": repo_name,
                        "type": "GITHUB_STANDARDS",
                        "description": "Add standard Pull Request template for contributor quality.",
                        "why": desc,
                        "difficulty": "Low",
                        "estimated_minutes": 10,
                        "agent_can_prepare": ".github/pull_request_template.md",
                        "requires_approval": True,
                    })
                elif itype == "MISSING_TOPICS":
                    opportunities.append({
                        "repository": repo_name,
                        "type": "DISCOVERABILITY",
                        "description": "Configure relevant tags/topics to boost GitHub search discoverability.",
                        "why": desc,
                        "difficulty": "Low",
                        "estimated_minutes": 5,
                        "agent_can_prepare": "Metadata update",
                        "requires_approval": True,
                    })

        # Record opportunities into database
        with self.db.get_connection() as conn:
            for opp in opportunities:
                conn.execute(
                    """
                    INSERT INTO contributions (repository_id, contribution_type, description, difficulty, estimated_minutes, status)
                    VALUES (?, ?, ?, ?, ?, 'IDENTIFIED')
                    """,
                    (repository_id, opp["type"], opp["description"], opp["difficulty"], opp["estimated_minutes"])
                )
            conn.commit()

        return opportunities

    def get_todays_opportunity(self) -> Optional[Dict[str, Any]]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT c.*, r.full_name as repo_name
                FROM contributions c
                LEFT JOIN repositories r ON c.repository_id = r.id
                WHERE c.status = 'IDENTIFIED'
                ORDER BY c.id DESC LIMIT 1
                """
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
        return None
