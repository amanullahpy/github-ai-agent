import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agent.classifier import IssueClassifier


class TestIssueClassification(unittest.TestCase):
    def test_classify_repository_issues(self):
        cat, status = IssueClassifier.classify("MISSING_README_INSTALLATION", "README.md")
        self.assertEqual(cat, "REPOSITORY")
        self.assertEqual(status, "FIXABLE")

        cat2, status2 = IssueClassifier.classify("MISSING_TOPICS", "metadata")
        self.assertEqual(cat2, "REPOSITORY")
        self.assertEqual(status2, "FIXABLE")

    def test_classify_code_issues_do_not_modify(self):
        cat, status = IssueClassifier.classify("POTENTIAL_N_PLUS_ONE_QUERY", "src/users.ts")
        self.assertEqual(cat, "CODE")
        self.assertEqual(status, "DO NOT MODIFY")

        cat2, status2 = IssueClassifier.classify("UNHANDLED_EXCEPTION", "app/main.py")
        self.assertEqual(cat2, "CODE")
        self.assertEqual(status2, "DO NOT MODIFY")

    def test_source_code_target_forced_to_code_level(self):
        # Even if issue type claims to be repository level, if resource is source code, force CODE and DO NOT MODIFY
        cat, status = IssueClassifier.classify("MISSING_README_INSTALLATION", "src/index.js")
        self.assertEqual(cat, "CODE")
        self.assertEqual(status, "DO NOT MODIFY")


if __name__ == "__main__":
    unittest.main()
