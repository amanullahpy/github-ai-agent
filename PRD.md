# GitHub AI Agent — PRD

**Version:** 1.0  
**Status:** MVP  
**Platform:** Local Windows Application / CLI  
**Primary Goal:** Maintain and improve the user's GitHub profile and repositories without modifying application source code automatically.

---

# 1. Product Overview

The GitHub AI Agent is a local-first AI automation system that continuously reviews the user's GitHub profile and repositories.

Its primary responsibility is **repository and profile quality management**, not application development.

The agent should:

1. Inspect the user's GitHub profile.
2. Inspect repositories one by one.
3. Evaluate repository quality and discoverability.
4. Read README files and GitHub configuration.
5. Identify repository-level problems.
6. Identify code-level problems without modifying code.
7. Suggest useful product/features improvements.
8. Generate structured Markdown reports.
9. Prepare fixes for repository-level problems.
10. Ask the user for approval before applying changes.
11. Apply approved repository-level changes to GitHub.
12. Track repository health over time.
13. Track GitHub contribution statistics.
14. Identify legitimate small contribution opportunities.
15. Help maintain consistent GitHub activity through useful work.
16. Avoid duplicate scans, duplicate issues, duplicate proposals, and duplicate commits.
17. Never fabricate activity or create meaningless changes purely to manipulate the contribution graph.

The system must be **human-in-the-loop**.

---

# 2. Core Principle

The GitHub Agent is a **GitHub Profile & Repository Maintainer**, not a coding agent.

The default rule is:

> **The agent may inspect source code and report code-level problems, but it must not modify source-code files.**

Repository-level improvements may be prepared and applied after user approval.

---

# 3. Scope of Responsibilities

## 3.1 Agent CAN

The agent may:

- Analyze GitHub profile.
- Analyze repositories.
- Analyze README files.
- Analyze repository descriptions.
- Analyze repository topics.
- Analyze GitHub metadata.
- Analyze GitHub configuration.
- Analyze documentation.
- Analyze templates.
- Analyze repository discoverability.
- Analyze project presentation.
- Suggest features.
- Identify code-level problems.
- Prepare documentation fixes.
- Prepare metadata fixes.
- Prepare GitHub configuration fixes.
- Create branches.
- Create commits.
- Create pull requests.
- Update approved repository-level files.
- Track contributions.
- Generate reports.

## 3.2 Agent MUST NOT Modify Automatically

The agent must not modify:

- Application source code.
- Backend business logic.
- Frontend code.
- Database logic.
- Authentication logic.
- API implementation.
- Tests.
- Dependencies.
- Configuration that can materially change application behavior.

These are classified as **Code-Level Issues** and must be reported only unless the user explicitly enables code-level permissions in the future.

---

# 4. Future Architecture

The system should be modular enough to become a larger personal GitHub management system.

```text
GitHub Agent
│
├── Profile Manager
│
├── Repository Scanner
│   ├── Metadata Scanner
│   ├── README Scanner
│   ├── Documentation Scanner
│   ├── GitHub Config Scanner
│   └── Code Analyzer
│
├── Issue Classifier
│   ├── Repository-Level
│   └── Code-Level
│
├── Feature Suggestion Engine
│
├── Solution Generator
│
├── Approval Manager
│
├── GitHub Updater
│
├── Contribution Manager
│
└── Reporting Engine
```

---

# 5. Recommended MVP Stack

Use the same lightweight/local-first philosophy as the Career Agent.

```text
Language:
Python 3.12+

GitHub:
GitHub REST API / GraphQL API where appropriate

Git:
Git CLI

AI:
Configurable LLM API (Gemini / OpenAI Compatible)

Database:
SQLite

Files:
Markdown + JSON

Scheduling:
Windows Task Scheduler

Version Control:
Git + GitHub

Interface:
CLI

Optional:
Playwright only where API functionality is insufficient
```

Do not require:

- Next.js
- React
- Supabase
- PostgreSQL
- Redis
- Docker
- Kubernetes
- Cloud infrastructure
- Dashboard

for MVP.

---

# 6. GitHub Profile Management

The agent should analyze the user's GitHub profile.

Check:

- Profile README
- Bio
- Name
- Website
- Social links
- Profile visibility
- Pinned repositories
- Repository presentation
- Contribution activity
- Public project quality

The agent should produce recommendations such as:

```text
GitHub Profile Health: 86/100

Profile README: Good
Bio: Needs improvement
Pinned repositories: Needs optimization
Website: Configured
Project discoverability: Good
```

Profile modifications require user approval.

---

# 7. Repository Discovery

The agent should retrieve the user's repositories using the GitHub API.

Classify repositories:

```text
ACTIVE
PORTFOLIO
EXPERIMENT
ARCHIVED
FORK
PRIVATE
PUBLIC
```

The agent should allow the user to configure repositories that should be:

```text
INCLUDE
EXCLUDE
HIGH_PRIORITY
IGNORE
```

Forks and archived repositories should generally be excluded unless explicitly configured.

---

# 8. Intelligent Repository Prioritization

The agent should not scan every repository equally every day.

Calculate a repository priority score.

Example factors:

```text
Portfolio importance
Recent activity
Public visibility
Pinned status
Recruiter relevance
Project quality
Recent changes
Previous scan age
```

Example:

```text
Priority 95 → Scan frequently
Priority 80 → Scan regularly
Priority 60 → Scan occasionally
Priority <40 → Low priority
```

The user should be able to configure:

```text
repositories_per_run = 2
```

---

# 9. Repository Scanner

For each selected repository, inspect:

## Metadata

- Repository name
- Description
- Topics
- Homepage
- Visibility
- License
- Default branch
- Repository settings
- Repository activity

## Documentation

- README
- CONTRIBUTING.md
- CODE_OF_CONDUCT.md
- SECURITY.md
- LICENSE
- Documentation folder

## GitHub Configuration

- `.github/`
- Issue templates
- Pull request templates
- GitHub Actions
- Dependabot configuration
- Workflows
- Security configuration

## Project Presentation

- Screenshots
- Demo link
- Installation instructions
- Usage instructions
- Tech stack
- Architecture explanation
- Features
- Project status

---

# 10. README Analysis

The agent should check whether the README contains useful sections.

Recommended structure:

```text
Project Title
Project Description
Demo
Screenshots
Features
Tech Stack
Architecture
Installation
Environment Variables
Usage
API Documentation
Project Structure
Roadmap
Contributing
License
```

The agent should not require every section for every project.
It should intelligently determine what is appropriate.

---

# 11. GitHub Discoverability Optimization

The agent should optimize repository discoverability.

Potential areas:

- Repository name
- Repository description
- Topics
- README structure
- Keywords
- Project screenshots
- Demo URL
- Technology references
- Documentation
- Project activity
- Repository organization

The system must NOT claim that these changes guarantee a specific GitHub search ranking.
The goal is to improve clarity, relevance, presentation, and discoverability.

---

# 12. Repository-Level Issues

Repository-level issues are problems the agent is allowed to fix after approval.

Examples:
- README is missing installation instructions.
- Repository description is empty.
- Relevant topics are missing.
- No demo URL is configured.
- No issue template exists.
- No pull request template exists.
- README lacks screenshots.
- License is missing.
- Contribution instructions are missing.
- Broken documentation link exists.
- GitHub profile README needs improvement.

These should be marked: `FIXABLE`.

---

# 13. Code-Level Issues

The agent should inspect source code when useful, but code-level findings must not be modified automatically.

Examples:
- Potential performance issue
- Potential security issue
- Poor component architecture
- Duplicated logic
- Missing error handling
- Potential database inefficiency
- Outdated API usage
- Missing tests
- Poor naming
- Technical debt

Store these as: `DO NOT MODIFY`.

---

# 14. Feature Suggestions

The agent should independently evaluate each repository and suggest useful improvements.

Feature suggestions are recommendations only.
The agent must not implement them automatically.
Status: `SUGGESTED`.

---

# 15. Standard GitHub Agent Folder

Each managed repository should contain:

```text
.github-agent/
│
├── scan-report.md
├── issues.md
├── solutions.md
└── feature-suggestions.md
```

If the `.github-agent` directory already exists, update the existing files rather than creating duplicates.

---

# 16. `scan-report.md`

Overall health report containing:
- Health score (0-100)
- Dimension scores (Documentation, Metadata, Standards, DX, Discoverability, Maintenance)
- Summary of opportunities and strengths

---

# 17. `issues.md`

Maintains two distinct, clear categories:
- `## Repository-Level Issues` (`FIXABLE`)
- `## Code-Level Issues` (`DO NOT MODIFY`)

---

# 18. `solutions.md`

Only repository-level solutions that can be safely prepared appear here.
Statuses: `PENDING`, `APPROVED`, `APPLIED`, `REJECTED`.

---

# 19. Approval Workflow

Every repository-level modification must go through interactive or automated approval.

CLI prompt:
- `[Y]` Approve
- `[N]` Reject
- `[V]` View diff
- `[S]` Skip

---

# 20. Git Workflow

Approved changes follow a safe Git workflow:
1. Create dedicated branch: `github-agent/<topic>`
2. Apply approved changes
3. Run validation & diff check
4. Commit with descriptive message
5. Push to remote
6. Create Pull Request if configured

Default branch is never directly modified unless explicitly configured.

---

# 21. Pull Requests

Agent creates PR with:
- Title
- Summary
- Changes list
- Reason
- Validation steps
- GitHub Agent note

Agent must not auto-merge PRs. Merging is always a user action.

---

# 22. Repository-Level Permission Model

Granular permission structure per repository:

```json
{
  "repository": "my-project",
  "permissions": {
    "read_repository": true,
    "read_code": true,
    "modify_readme": true,
    "modify_metadata": true,
    "modify_topics": true,
    "modify_github_templates": true,
    "modify_docs": true,
    "modify_source_code": false,
    "modify_tests": false,
    "modify_dependencies": false,
    "create_branch": true,
    "create_commit": true,
    "create_pull_request": true,
    "merge_pull_request": false
  }
}
```

Source code modification defaults strictly to `false`.

---

# 23. Contribution Manager

Track legitimate GitHub activity:
- Commits, PRs, issues, code reviews
- Active repositories
- Consistency and cadence

---

# 24. Legitimate Daily Contribution Opportunities

Identify genuine small tasks:
- Setup instructions, broken link fixes, issue/PR templates, metadata/topic additions.
- Never create meaningless commits solely to manipulate the contribution graph.

---

# 25. Contribution Goal

> **Consistent, genuine GitHub activity that demonstrates useful engineering and documentation work.**

---

# 26. Daily Workflow

Orchestrates priority selection, cache checks, scanning, issue classification, solution generation, approval, commit/PR creation, and reporting.

---

# 27. Scan Caching / Idempotency

Compute repository state fingerprint:
```text
scan_hash = SHA256(metadata_hash + README_hash + config_hash + structure_hash)
```
If unchanged, skip expensive analysis.

---

# 28. Issue Deduplication

Deterministic fingerprints:
```text
issue_hash = SHA256(repo + type + normalized_description + target_file)
```
Existing issues are updated (`last_seen_at`) rather than duplicated.

---

# 29. Solution Deduplication

```text
solution_hash = SHA256(issue_hash + proposed_change + prompt_version)
```

---

# 30. Commit Deduplication

```text
commit_fingerprint = SHA256(repo + branch + change_hash)
```
Avoid duplicate commits for previously applied changes.

---

# 31. AI Cost Optimization

Deterministic heuristic checks run before invoking LLM calls.

---

# 32. AI Usage Tracking

Log model, tokens (input/output), cost estimate, latency, and success in database.

---

# 33. Error Handling

Classified errors:
`GITHUB_API_ERROR`, `AUTHENTICATION_REQUIRED`, `RATE_LIMIT`, `NETWORK_ERROR`, `REPOSITORY_ACCESS_ERROR`, `GIT_ERROR`, `AI_ERROR`, `FILE_ERROR`, `VALIDATION_ERROR`, `PERMISSION_ERROR`.

---

# 34. Retry Policy

Exponential backoff for API/network/AI errors.
Stop and prompt user on conflicts, permission errors, and auth failures.
Never bypass GitHub rate limits.

---

# 35. Security

- Secrets stored only in `.env` / environment variables.
- `.env` in `.gitignore`.
- Fine-grained GitHub tokens with minimum required permissions.

---

# 36. Privacy

- Reports kept local by default.
- Never send `.env`, passwords, or private keys to LLM.
- Redact sensitive data before AI analysis.

---

# 37. Secrets Detection

Pre-commit regex scanners check for tokens, private keys, API credentials. If detected, commit is aborted immediately.

---

# 38. Logging

Formatted timestamps, run IDs, and levels written to both console and `logs/github-agent.log`.

---

# 39. CLI Interface

```bash
python github_agent.py scan [repo]
python github_agent.py profile
python github_agent.py repos
python github_agent.py issues [--repo=NAME]
python github_agent.py solutions [--status=PENDING]
python github_agent.py contributions
python github_agent.py approve [solution_id]
python github_agent.py status
python github_agent.py run [--limit=2]
```

---

# 40. Suggested Folder Structure

```text
github-agent/
│
├── github_agent.py
├── config.py
├── requirements.txt
├── .env
├── .gitignore
│
├── agent/
│   ├── scanner.py
│   ├── profile.py
│   ├── prioritizer.py
│   ├── classifier.py
│   ├── issue_manager.py
│   ├── solution_manager.py
│   ├── contribution.py
│   ├── approval.py
│   └── reporter.py
│
├── github/
│   ├── client.py
│   ├── repositories.py
│   ├── metadata.py
│   ├── branches.py
│   ├── commits.py
│   └── pull_requests.py
│
├── ai/
│   ├── provider.py
│   ├── prompts.py
│   └── cache.py
│
├── database/
│   ├── db.py
│   ├── models.py
│   └── migrations.py
│
├── data/
│   ├── config.json
│   └── github-agent.db
│
├── reports/
│
├── tests/
│   ├── test_duplicates.py
│   ├── test_hashing.py
│   ├── test_permissions.py
│   ├── test_rate_limits.py
│   └── test_issue_classification.py
│
└── logs/
    └── github-agent.log
```

---

# 41. SQLite Database Tables

`github_profile`, `repositories`, `repository_scans`, `repository_issues`, `feature_suggestions`, `solutions`, `solution_changes`, `approvals`, `contributions`, `agent_runs`, `github_actions`, `ai_usage`, `settings`.

---

# 42. Database Constraints

Database-level `UNIQUE` constraints on:
- `repositories.github_repo_id`
- `repositories.full_name`
- `repository_scans.scan_hash`
- `repository_issues.issue_hash`
- `feature_suggestions.suggestion_hash`
- `solutions.solution_hash`
- `github_actions.action_hash`

---

# 43. Change Tracking

Record before/after hashes, diffs, approval state, applied state.

---

# 44. Rollback

Preserve previous hashes, branch details, commit SHA for reversible actions.

---

# 45. Repository Health Score

Configurable scoring model:
- Documentation: 20%
- Metadata: 10%
- Discoverability: 15%
- GitHub Standards: 15%
- Developer Experience: 15%
- Maintenance: 15%
- Presentation: 10%

---

# 46. Profile Health Score

Evaluates profile completeness, README, pinned repositories, portfolio relevance, discoverability.

---

# 47. Daily Contribution Recommendation

Generates clear, actionable, high-value opportunities with estimated time, rationale, and diff preview.

---

# 48. Repository Selection Intelligence

Prioritizes public, active, portfolio, pinned repositories. Deprioritizes archived, empty, and fork repos.

---

# 49. No-Code-Modification Enforcement

Defense-in-depth:
1. Agent prompt directive
2. Permission config setting (`modify_source_code: false`)
3. Solution engine file-type validation
4. Git pre-commit diff inspection

---

# 50. Unexpected Change Protection

Diff verification checks actual staged files vs expected target files. Any mismatch halts the commit.

---

# 51. GitHub API Rate Limits

Respects GitHub rate limit headers (`x-ratelimit-remaining`, `x-ratelimit-reset`). Backs off gracefully.

---

# 52. Idempotent Daily Execution

Multiple consecutive runs without changes yield identical database state and zero duplicate commits/PRs.

---

# 53. Complete Daily Workflow Pipeline

End-to-end execution flow with security, deduplication, user approval, and reporting.

---

# 54. MVP Must-Have Features

Covers complete CLI, scanners, classifier, diff viewer, git manager, PR creator, database, test suite.

---

# 55. Phase 2

Advanced README auto-generation, screenshot assistance, topic suggestions, PR review analysis.

---

# 56. Phase 3

Integration with personal career systems (Career Agent & LinkedIn Agent).

---

# 57. Definition of Done — MVP

28 explicit verification items validating CLI execution, no-source-code safety, deduplication, and error handling.

---

# 58. Primary Product Principle

**Repository Quality > Activity Quantity**  
**Real Contributions > Artificial Contributions**  
**Safety > Autonomy**
