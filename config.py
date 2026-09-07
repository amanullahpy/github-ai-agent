import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

# Base paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
REPORTS_DIR = BASE_DIR / "reports"

# Ensure runtime directories exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")
except ImportError:
    env_file = BASE_DIR / ".env"
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip("'\""))



class Config:
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
    GITHUB_USERNAME: str = os.getenv("GITHUB_USERNAME", "")

    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "gemini")
    AI_API_KEY: str = os.getenv("AI_API_KEY", "")
    AI_MODEL: str = os.getenv("AI_MODEL", "gemini-2.5-flash")
    AI_BASE_URL: str = os.getenv("AI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta")

    DB_PATH: Path = DATA_DIR / "github-agent.db"
    LOG_FILE: Path = LOGS_DIR / "github-agent.log"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    CONFIG_FILE: Path = DATA_DIR / "config.json"

    @classmethod
    def load_json_config(cls) -> Dict[str, Any]:
        if cls.CONFIG_FILE.exists():
            with open(cls.CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    @classmethod
    def get_repositories_per_run(cls) -> int:
        json_cfg = cls.load_json_config()
        env_val = os.getenv("REPOSITORIES_PER_RUN")
        if env_val and env_val.isdigit():
            return int(env_val)
        return json_cfg.get("repositories_per_run", 5)


    @classmethod
    def get_default_permissions(cls) -> Dict[str, bool]:
        json_cfg = cls.load_json_config()
        defaults = {
            "read_repository": True,
            "read_code": True,
            "modify_readme": True,
            "modify_metadata": True,
            "modify_topics": True,
            "modify_github_templates": True,
            "modify_docs": True,
            "modify_source_code": False,
            "modify_tests": False,
            "modify_dependencies": False,
            "create_branch": True,
            "create_commit": True,
            "create_pull_request": True,
            "merge_pull_request": False,
        }
        custom = json_cfg.get("default_permissions", {})
        defaults.update(custom)
        # Defense-in-depth: Never allow modify_source_code by default
        defaults["modify_source_code"] = False
        return defaults

    @classmethod
    def get_protected_patterns(cls) -> List[str]:
        json_cfg = cls.load_json_config()
        return json_cfg.get(
            "protected_file_patterns",
            ["*.py", "*.ts", "*.js", "*.tsx", "*.jsx", "*.go", "*.rs", "*.java", "*.c", "*.cpp", "*.cs", "*.sql"]
        )

    @classmethod
    def get_allowed_fixable_patterns(cls) -> List[str]:
        json_cfg = cls.load_json_config()
        return json_cfg.get(
            "allowed_fixable_patterns",
            ["README.md", "readme.md", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md", "SECURITY.md", "LICENSE", ".github/**"]
        )
