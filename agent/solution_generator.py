import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from database import Database, get_db
from database.models import Solution
from .solution_manager import SolutionManager
from ai.provider import AIProvider
from ai.prompts import README_ENHANCEMENT_PROMPT
from config import Config

logger = logging.getLogger("github-agent.solution_generator")


class SolutionGenerator:
    def __init__(
        self,
        db: Optional[Database] = None,
        solution_manager: Optional[SolutionManager] = None,
        ai_provider: Optional[AIProvider] = None,
    ):
        self.db = db or get_db()
        self.solution_mgr = solution_manager or SolutionManager(self.db)
        self.ai = ai_provider or AIProvider()

    def generate_solution_for_issue(
        self,
        repository_id: int,
        repo_full_name: str,
        issue: Dict[str, Any],
        current_readme: str = "",
        repo_metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Solution]:
        issue_id = issue["id"]
        issue_type = issue["issue_type"]
        issue_hash = issue["issue_hash"]
        owner, repo_name = repo_full_name.split("/")
        year = datetime.now(timezone.utc).year
        meta = repo_metadata or {}
        tech_stack = meta.get("language") or "Fullstack / JavaScript / Python"
        description = meta.get("description") or "Open source project"

        if issue_type == "MISSING_PR_TEMPLATE":
            target_file = ".github/pull_request_template.md"
            content = """## Description
<!-- Briefly describe the changes introduced in this pull request -->

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Documentation update
- [ ] Refactoring / code quality improvement

## Checklist
- [ ] Code follows the project's guidelines
- [ ] Self-review of changes performed
- [ ] Documentation updated where appropriate
- [ ] Changes tested locally
"""
            return self.solution_mgr.create_solution(
                issue_id=issue_id,
                repository_id=repository_id,
                issue_hash=issue_hash,
                title="Add Pull Request Template",
                target_file=target_file,
                original_content="",
                new_content=content,
                risk_level="LOW",
            )

        elif issue_type == "MISSING_ISSUE_TEMPLATE":
            target_file = ".github/ISSUE_TEMPLATE/bug_report.md"
            content = """---
name: Bug report
about: Create a report to help improve this project
title: ''
labels: bug
assignees: ''
---

## Description
A clear and concise description of what the bug is.

## Steps to Reproduce
1. Go to '...'
2. Execute '....'
3. See error

## Expected Behavior
A clear and concise description of what you expected to happen.

## Environment
- OS: [e.g. Windows, macOS, Linux]
- Runtime/Version: [e.g. Node 20, Python 3.12]
"""
            return self.solution_mgr.create_solution(
                issue_id=issue_id,
                repository_id=repository_id,
                issue_hash=issue_hash,
                title="Add Standard Bug Report Template",
                target_file=target_file,
                original_content="",
                new_content=content,
                risk_level="LOW",
            )

        elif issue_type == "MISSING_README_INSTALLATION":
            target_file = "README.md"
            # Attempt AI-powered custom generation
            ai_prompt = README_ENHANCEMENT_PROMPT.format(
                repo_name=repo_name,
                description=description,
                tech_stack=tech_stack,
                readme_snippet=current_readme[:600],
                section_type="Installation & Setup instructions",
            )
            ai_section = self.ai.generate(
                prompt=ai_prompt,
                operation="readme_installation_generation",
                repository_id=repository_id,
                context={"repo_name": repo_name, "tech_stack": tech_stack}
            )

            if ai_section and "##" in ai_section and len(ai_section.strip()) > 30:
                print(f"      [AI] Generated custom Installation section via {self.ai.model}")
                install_section = f"\n\n{ai_section.strip()}\n"
            else:
                install_section = f"""

## 🚀 Installation & Setup

```bash
# Clone the repository
git clone https://github.com/{repo_full_name}.git
cd {repo_name}

# Install dependencies
npm install # or pip install -r requirements.txt
```
"""
            new_readme = (current_readme + install_section).strip() + "\n"
            return self.solution_mgr.create_solution(
                issue_id=issue_id,
                repository_id=repository_id,
                issue_hash=issue_hash,
                title="Add Installation & Setup section to README",
                target_file=target_file,
                original_content=current_readme,
                new_content=new_readme,
                risk_level="LOW",
            )

        elif issue_type == "MISSING_README_USAGE":
            target_file = "README.md"
            # Attempt AI-powered custom generation
            ai_prompt = README_ENHANCEMENT_PROMPT.format(
                repo_name=repo_name,
                description=description,
                tech_stack=tech_stack,
                readme_snippet=current_readme[:600],
                section_type="Usage & Quickstart guide",
            )
            ai_section = self.ai.generate(
                prompt=ai_prompt,
                operation="readme_usage_generation",
                repository_id=repository_id,
                context={"repo_name": repo_name, "tech_stack": tech_stack}
            )

            if ai_section and "##" in ai_section and len(ai_section.strip()) > 30:
                print(f"      [AI] Generated custom Usage section via {self.ai.model}")
                usage_section = f"\n\n{ai_section.strip()}\n"
            else:
                usage_section = f"""

## 💻 Usage

```bash
# Run / start the project
npm start # or python main.py
```
"""
            new_readme = (current_readme + usage_section).strip() + "\n"
            return self.solution_mgr.create_solution(
                issue_id=issue_id,
                repository_id=repository_id,
                issue_hash=issue_hash,
                title="Add Usage section to README",
                target_file=target_file,
                original_content=current_readme,
                new_content=new_readme,
                risk_level="LOW",
            )

        elif issue_type == "MISSING_LICENSE":
            target_file = "LICENSE"
            author = owner or Config.GITHUB_USERNAME or "Maintainer"
            license_content = f"""MIT License

Copyright (c) {year} {author}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
            return self.solution_mgr.create_solution(
                issue_id=issue_id,
                repository_id=repository_id,
                issue_hash=issue_hash,
                title="Add standard MIT License",
                target_file=target_file,
                original_content="",
                new_content=license_content,
                risk_level="LOW",
            )

        return None
