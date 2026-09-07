from typing import Dict, Any, Tuple
from config import Config


class IssueClassifier:
    REPOSITORY_ISSUE_TYPES = {
        "MISSING_README_INSTALLATION",
        "MISSING_README_USAGE",
        "MISSING_README_SCREENSHOTS",
        "MISSING_DESCRIPTION",
        "MISSING_TOPICS",
        "MISSING_HOMEPAGE",
        "MISSING_LICENSE",
        "MISSING_ISSUE_TEMPLATE",
        "MISSING_PR_TEMPLATE",
        "MISSING_CONTRIBUTING",
        "BROKEN_DOC_LINK",
    }

    CODE_ISSUE_TYPES = {
        "POTENTIAL_N_PLUS_ONE_QUERY",
        "UNHANDLED_EXCEPTION",
        "HARDCODED_CREDENTIAL",
        "PERFORMANCE_BOTTLENECK",
        "DUPLICATE_LOGIC",
        "MISSING_TEST_COVERAGE",
        "OUTDATED_API_USAGE",
        "STRUCTURAL_TECH_DEBT",
    }

    @classmethod
    def is_source_code(cls, file_path: str) -> bool:
        if not file_path:
            return False
        patterns = Config.get_protected_patterns()
        for pat in patterns:
            ext = pat.replace("*", "")
            if file_path.endswith(ext):
                return True
        return False

    @classmethod
    def classify(cls, issue_type: str, affected_resource: str) -> Tuple[str, str]:
        """
        Returns (category, status)
        category: 'REPOSITORY' or 'CODE'
        status: 'FIXABLE' or 'DO NOT MODIFY'
        """
        # Multi-layer safety: If affected resource is a source code file, it MUST be CODE-level and DO NOT MODIFY
        if cls.is_source_code(affected_resource) or issue_type in cls.CODE_ISSUE_TYPES:
            return "CODE", "DO NOT MODIFY"

        if issue_type in cls.REPOSITORY_ISSUE_TYPES:
            return "REPOSITORY", "FIXABLE"

        # Default fallback safety
        return "CODE", "DO NOT MODIFY"
