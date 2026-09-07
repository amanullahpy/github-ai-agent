import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.db import Database
from agent.issue_manager import IssueManager
from agent.solution_manager import SolutionManager


class TestDuplicates(unittest.TestCase):
    def test_issue_deduplication(self):
        with tempfile.TemporaryDirectory() as tmp_path:
            db = Database(Path(tmp_path) / "test_dedup.db")
            with db.get_connection() as conn:
                conn.execute("INSERT INTO repositories (id, github_repo_id, full_name, name) VALUES (1, 101, 'user/test', 'test')")
                conn.commit()

            mgr = IssueManager(db)

            # First record
            i1 = mgr.record_issue(1, "user/test", "MISSING_README_INSTALLATION", "Missing setup", "README.md")
            # Duplicate record
            i2 = mgr.record_issue(1, "user/test", "MISSING_README_INSTALLATION", "Missing setup", "README.md")

            self.assertEqual(i1.id, i2.id)
            self.assertEqual(i1.issue_hash, i2.issue_hash)

            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT count(*) as cnt FROM repository_issues")
                self.assertEqual(cursor.fetchone()["cnt"], 1)

    def test_solution_deduplication(self):
        with tempfile.TemporaryDirectory() as tmp_path:
            db = Database(Path(tmp_path) / "test_sol_dedup.db")
            with db.get_connection() as conn:
                conn.execute("INSERT INTO repositories (id, github_repo_id, full_name, name) VALUES (1, 102, 'user/test2', 'test2')")
                conn.execute(
                    "INSERT INTO repository_issues (id, repository_id, category, issue_type, description, affected_resource, issue_hash) "
                    "VALUES (1, 1, 'REPOSITORY', 'MISSING_README_INSTALLATION', 'Missing setup', 'README.md', 'hash_issue_1')"
                )
                conn.commit()

            mgr = SolutionManager(db)

            s1 = mgr.create_solution(1, 1, "issuehash", "Add Install", "README.md", "# Old", "# Old\n## Install\nrun")
            s2 = mgr.create_solution(1, 1, "issuehash", "Add Install", "README.md", "# Old", "# Old\n## Install\nrun")

            self.assertEqual(s1.id, s2.id)
            self.assertEqual(s1.solution_hash, s2.solution_hash)

            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT count(*) as cnt FROM solutions")
                self.assertEqual(cursor.fetchone()["cnt"], 1)



if __name__ == "__main__":
    unittest.main()
