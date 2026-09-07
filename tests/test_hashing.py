import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agent.issue_manager import IssueManager
from agent.solution_manager import SolutionManager
from agent.scanner import RepositoryScanner


class TestHashing(unittest.TestCase):
    def test_issue_hash_is_deterministic(self):
        h1 = IssueManager.compute_issue_hash("user/repo", "MISSING_README_INSTALLATION", "README is missing installation", "README.md")
        h2 = IssueManager.compute_issue_hash("user/repo", "MISSING_README_INSTALLATION", "README is missing   installation", "README.md")
        self.assertEqual(h1, h2)
        self.assertEqual(len(h1), 64)

    def test_solution_hash_is_deterministic(self):
        issue_hash = "abc123456"
        change = "## Installation\n\nRun npm install"
        s1 = SolutionManager.compute_solution_hash(issue_hash, change)
        s2 = SolutionManager.compute_solution_hash(issue_hash, "## Installation\n\nRun   npm install")
        self.assertEqual(s1, s2)
        self.assertEqual(len(s1), 64)

    def test_scan_hash_changes_with_readme(self):
        meta = {"name": "test-repo", "description": "Test", "topics": ["python"]}
        files = [".github/workflows/ci.yml"]
        h1 = RepositoryScanner.compute_scan_hash(meta, "# Hello", files)
        h2 = RepositoryScanner.compute_scan_hash(meta, "# Hello World", files)
        self.assertNotEqual(h1, h2)


if __name__ == "__main__":
    unittest.main()
