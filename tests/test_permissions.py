import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from github.commits import CommitService
from agent.solution_manager import SolutionManager


class TestPermissions(unittest.TestCase):
    def test_is_source_code_file(self):
        self.assertTrue(CommitService.is_source_code_file("src/app.py"))
        self.assertTrue(CommitService.is_source_code_file("frontend/component.tsx"))
        self.assertTrue(CommitService.is_source_code_file("api/main.go"))
        self.assertFalse(CommitService.is_source_code_file("README.md"))
        self.assertFalse(CommitService.is_source_code_file(".github/pull_request_template.md"))

    def test_is_allowed_file(self):
        self.assertTrue(CommitService.is_allowed_file("README.md"))
        self.assertTrue(CommitService.is_allowed_file("LICENSE"))
        self.assertTrue(CommitService.is_allowed_file(".github/workflows/ci.yml"))
        self.assertFalse(CommitService.is_allowed_file("src/logic.py"))

    def test_solution_creation_fails_on_source_code(self):
        from database.db import Database
        with tempfile.TemporaryDirectory() as tmp_dir:
            test_db = Database(Path(tmp_dir) / "test.db")
            mgr = SolutionManager(test_db)

            with self.assertRaises(PermissionError) as ctx:
                mgr.create_solution(
                    issue_id=1,
                    repository_id=1,
                    issue_hash="hash1",
                    title="Refactor query",
                    target_file="src/database.py",
                    original_content="SELECT *",
                    new_content="SELECT id",
                )
            self.assertIn("Safety Violation", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
