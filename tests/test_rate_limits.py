import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from github.client import GitHubClient


class TestRateLimits(unittest.TestCase):
    def test_rate_limit_header_check(self):
        client = GitHubClient(token="dummy_token")
        mock_resp = MagicMock()
        mock_resp.headers = {
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": "1700000000",
        }
        # Should safely check without throwing unhandled exceptions
        client._check_rate_limit(mock_resp)


if __name__ == "__main__":
    unittest.main()
