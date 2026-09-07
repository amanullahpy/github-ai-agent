# GitHub AI Agent 🤖

> A local-first, human-in-the-loop AI system that continuously reviews, maintains, and elevates your GitHub profile and repositories **without modifying application source code**.

---

## 🌟 Core Principles

1. **Repository Quality > Activity Quantity**: Focus on genuine documentation, discoverability, and standards rather than empty commits.
2. **Strict Safety & No Code Modification**: The agent is permitted to inspect source code and report issues, but is strictly prohibited from modifying source code files.
3. **Human-in-the-loop**: All repository-level changes require explicit review and approval with a clear diff.
4. **Deterministic & Idempotent**: Prevents duplicate scans, duplicate issues, duplicate proposals, and duplicate commits.

---

## 🚀 Quickstart

### 1. Installation

```bash
# Clone or navigate to the project directory
cd github-agent

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Copy `.env.example` to `.env` and configure your credentials:

```bash
copy .env.example .env
```

Edit `.env`:
```ini
GITHUB_TOKEN=ghp_your_github_personal_access_token
GITHUB_USERNAME=your_username
AI_PROVIDER=gemini
AI_API_KEY=your_gemini_or_openai_api_key
```

*(Note: The agent can run with deterministic heuristics even without an AI key).*

---

## 🛠️ CLI Usage

### Full Automated Pipeline (Recommended)

Run the entire end-to-end maintainer workflow automatically in one command:

```bash
# Automated run: Scans top priority repositories, detects issues, generates solutions & reports
python github_agent.py run

# Target a specific repository (Public or Private)
python github_agent.py run --repo amanullahpy/my-private-repo

# Fully automated: Scan, generate fixes, approve, create branch, commit & open Pull Requests
python github_agent.py run --limit 2 --apply --yes
```

### Individual Subcommands

```bash
# Check system status, database, and configuration
python github_agent.py status

# Inspect GitHub Profile and get actionable recommendations
python github_agent.py profile

# Discover and prioritize ALL repositories (both Public & Private)
python github_agent.py repos

# Scan a specific repository
python github_agent.py scan owner/repo-name

# View detected issues (separated into FIXABLE vs DO NOT MODIFY)
python github_agent.py issues

# Inspect proposed solutions
python github_agent.py solutions

# Interactively approve or reject proposed changes with unified diffs
python github_agent.py approve [solution_id]

# View today's legitimate contribution opportunity
python github_agent.py contributions
```


---

## 📁 Repository Structure

```text
github-agent/
│
├── github_agent.py          # CLI entry point
├── config.py                # Configuration loader & permission guards
├── requirements.txt         # Lightweight dependencies
├── PRD.md                   # 58-section Product Requirements Document
├── .env.example             # Safe environment template
├── .gitignore               # Secrets and cache exclusions
│
├── agent/                   # Intelligence core
│   ├── scanner.py           # Multi-dimensional repository health scoring
│   ├── profile.py           # Profile completeness and optimization
│   ├── prioritizer.py       # Priority algorithm (portfolio, activity, scan age)
│   ├── classifier.py        # Separates repository-level vs code-level issues
│   ├── issue_manager.py     # Deterministic SHA256 issue deduplication
│   ├── solution_manager.py  # Safe diff generator & solution cache
│   ├── contribution.py      # Legitimate contribution opportunity finder
│   ├── approval.py          # Interactive CLI approval workflow
│   └── reporter.py          # .github-agent/ markdown reports generator
│
├── github/                  # GitHub API and Git client
│   ├── client.py            # REST client with rate-limit and backoff
│   ├── repositories.py      # Repositories & file content service
│   ├── metadata.py          # Topics, description, homepage manager
│   ├── branches.py          # Safe branch creation (`github-agent/...`)
│   ├── commits.py           # Defense-in-depth secret & change validation
│   └── pull_requests.py     # Non-merging PR creator
│
├── ai/                      # AI provider abstraction
│   ├── provider.py          # Gemini & OpenAI-compatible LLM handler
│   ├── prompts.py           # System prompts enforcing safety directives
│   └── cache.py             # Deterministic prompt cache & usage logger
│
├── database/                # SQLite storage layer
│   ├── db.py                # Thread-safe SQLite connection
│   ├── models.py            # Typed dataclasses
│   └── migrations.py        # Schema with UNIQUE constraint deduplication
│
├── data/                    # Local storage & settings
│   ├── config.json          # Scoring weights & permission models
│   └── github-agent.db      # SQLite database
│
├── reports/                 # Generated repository reports
├── tests/                   # Automated safety & integrity tests
└── logs/                    # Runtime logs
```

---

## 🔒 Defense-in-Depth Safety Guardrails

| Layer | Mechanism | Protection |
|---|---|---|
| **Prompt Level** | Strict system instruction | Instructs AI model never to modify source-code files |
| **Configuration** | `modify_source_code = False` | Application-level permission flag hardcoded to False |
| **Solution Manager** | File extension validator | Blocks creation of solutions targeting source files (`.py`, `.ts`, `.js`, etc.) |
| **Git Pre-Commit** | Staged diff & secret scanner | Aborts commits containing unexpected files, private keys, or API tokens |
| **Pull Request** | Non-merging rule | Agent creates PRs but never automatically merges them |

---

## 🧪 Running Tests

```bash
pytest tests/
```
