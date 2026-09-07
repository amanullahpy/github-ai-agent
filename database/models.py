from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List


@dataclass
class GitHubProfile:
    id: Optional[int] = None
    username: str = ""
    name: Optional[str] = None
    bio: Optional[str] = None
    website: Optional[str] = None
    public_repos: int = 0
    followers: int = 0
    following: int = 0
    profile_readme_present: bool = False
    profile_health_score: float = 0.0
    scanned_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Repository:
    id: Optional[int] = None
    github_repo_id: int = 0
    full_name: str = ""
    name: str = ""
    description: Optional[str] = None
    homepage: Optional[str] = None
    default_branch: str = "main"
    is_private: bool = False
    is_fork: bool = False
    is_archived: bool = False
    stars_count: int = 0
    forks_count: int = 0
    open_issues_count: int = 0
    topics: List[str] = field(default_factory=list)
    license_key: Optional[str] = None
    classification: str = "ACTIVE"  # ACTIVE, PORTFOLIO, EXPERIMENT, ARCHIVED, FORK, PRIVATE, PUBLIC
    priority_score: float = 50.0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_scanned_at: Optional[datetime] = None


@dataclass
class RepositoryScan:
    id: Optional[int] = None
    repository_id: int = 0
    scan_hash: str = ""
    health_score: float = 0.0
    documentation_score: float = 0.0
    metadata_score: float = 0.0
    standards_score: float = 0.0
    dx_score: float = 0.0
    discoverability_score: float = 0.0
    maintenance_score: float = 0.0
    presentation_score: float = 0.0
    summary: str = ""
    scanned_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class RepositoryIssue:
    id: Optional[int] = None
    repository_id: int = 0
    category: str = "REPOSITORY"  # REPOSITORY or CODE
    issue_type: str = ""
    description: str = ""
    affected_resource: str = ""
    severity: str = "LOW"  # LOW, MEDIUM, HIGH, CRITICAL
    status: str = "FIXABLE"  # FIXABLE for repository-level, DO NOT MODIFY for code-level
    issue_hash: str = ""
    first_seen_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_seen_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class FeatureSuggestion:
    id: Optional[int] = None
    repository_id: int = 0
    title: str = ""
    description: str = ""
    priority: str = "MEDIUM"
    expected_benefit: str = ""
    suggested_implementation: str = ""
    suggestion_hash: str = ""
    status: str = "SUGGESTED"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Solution:
    id: Optional[int] = None
    issue_id: int = 0
    repository_id: int = 0
    title: str = ""
    proposed_change: str = ""
    target_file: str = ""
    diff: str = ""
    risk_level: str = "LOW"
    solution_hash: str = ""
    status: str = "PENDING"  # PENDING, APPROVED, APPLIED, REJECTED
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class SolutionChange:
    id: Optional[int] = None
    solution_id: int = 0
    file_path: str = ""
    change_type: str = "UPDATE"
    before_hash: Optional[str] = None
    after_hash: Optional[str] = None
    diff: str = ""
    approved: bool = False
    applied: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Approval:
    id: Optional[int] = None
    solution_id: int = 0
    action: str = "PENDING"  # APPROVE, REJECT, SKIP
    notes: Optional[str] = None
    decided_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Contribution:
    id: Optional[int] = None
    repository_id: Optional[int] = None
    contribution_type: str = ""
    description: str = ""
    difficulty: str = "LOW"
    estimated_minutes: int = 15
    status: str = "IDENTIFIED"
    recorded_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class AgentRun:
    id: Optional[int] = None
    run_id: str = ""
    status: str = "RUNNING"  # RUNNING, COMPLETED, FAILED
    repositories_scanned: int = 0
    issues_found: int = 0
    solutions_proposed: int = 0
    changes_applied: int = 0
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    ended_at: Optional[datetime] = None
    error_message: Optional[str] = None


@dataclass
class GitHubAction:
    id: Optional[int] = None
    repository_id: int = 0
    action_type: str = ""  # BRANCH_CREATE, COMMIT, PULL_REQUEST
    branch_name: Optional[str] = None
    commit_sha: Optional[str] = None
    pr_number: Optional[int] = None
    action_hash: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class AIUsage:
    id: Optional[int] = None
    operation: str = ""
    repository_id: Optional[int] = None
    model: str = ""
    input_hash: str = ""
    prompt_version: str = "1.0"
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost: float = 0.0
    success: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
