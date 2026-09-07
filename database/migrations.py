import sqlite3

MIGRATION_SQL = """
CREATE TABLE IF NOT EXISTS github_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    name TEXT,
    bio TEXT,
    website TEXT,
    public_repos INTEGER DEFAULT 0,
    followers INTEGER DEFAULT 0,
    following INTEGER DEFAULT 0,
    profile_readme_present BOOLEAN DEFAULT 0,
    profile_health_score REAL DEFAULT 0.0,
    scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS repositories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    github_repo_id INTEGER NOT NULL UNIQUE,
    full_name TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT,
    homepage TEXT,
    default_branch TEXT DEFAULT 'main',
    is_private BOOLEAN DEFAULT 0,
    is_fork BOOLEAN DEFAULT 0,
    is_archived BOOLEAN DEFAULT 0,
    stars_count INTEGER DEFAULT 0,
    forks_count INTEGER DEFAULT 0,
    open_issues_count INTEGER DEFAULT 0,
    topics TEXT,
    license_key TEXT,
    classification TEXT DEFAULT 'ACTIVE',
    priority_score REAL DEFAULT 50.0,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    last_scanned_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS repository_scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repository_id INTEGER NOT NULL,
    scan_hash TEXT NOT NULL UNIQUE,
    health_score REAL DEFAULT 0.0,
    documentation_score REAL DEFAULT 0.0,
    metadata_score REAL DEFAULT 0.0,
    standards_score REAL DEFAULT 0.0,
    dx_score REAL DEFAULT 0.0,
    discoverability_score REAL DEFAULT 0.0,
    maintenance_score REAL DEFAULT 0.0,
    presentation_score REAL DEFAULT 0.0,
    summary TEXT,
    scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(repository_id) REFERENCES repositories(id)
);

CREATE TABLE IF NOT EXISTS repository_issues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repository_id INTEGER NOT NULL,
    category TEXT NOT NULL, -- 'REPOSITORY' or 'CODE'
    issue_type TEXT NOT NULL,
    description TEXT NOT NULL,
    affected_resource TEXT NOT NULL,
    severity TEXT DEFAULT 'LOW',
    status TEXT DEFAULT 'FIXABLE', -- 'FIXABLE' or 'DO NOT MODIFY'
    issue_hash TEXT NOT NULL UNIQUE,
    first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(repository_id) REFERENCES repositories(id)
);

CREATE TABLE IF NOT EXISTS feature_suggestions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repository_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    priority TEXT DEFAULT 'MEDIUM',
    expected_benefit TEXT,
    suggested_implementation TEXT,
    suggestion_hash TEXT NOT NULL UNIQUE,
    status TEXT DEFAULT 'SUGGESTED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(repository_id) REFERENCES repositories(id)
);

CREATE TABLE IF NOT EXISTS solutions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    issue_id INTEGER NOT NULL,
    repository_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    proposed_change TEXT NOT NULL,
    target_file TEXT NOT NULL,
    diff TEXT NOT NULL,
    risk_level TEXT DEFAULT 'LOW',
    solution_hash TEXT NOT NULL UNIQUE,
    status TEXT DEFAULT 'PENDING', -- PENDING, APPROVED, APPLIED, REJECTED
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(issue_id) REFERENCES repository_issues(id),
    FOREIGN KEY(repository_id) REFERENCES repositories(id)
);

CREATE TABLE IF NOT EXISTS solution_changes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    solution_id INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    change_type TEXT DEFAULT 'UPDATE',
    before_hash TEXT,
    after_hash TEXT,
    diff TEXT,
    approved BOOLEAN DEFAULT 0,
    applied BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(solution_id) REFERENCES solutions(id)
);

CREATE TABLE IF NOT EXISTS approvals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    solution_id INTEGER NOT NULL,
    action TEXT NOT NULL, -- APPROVE, REJECT, SKIP
    notes TEXT,
    decided_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(solution_id) REFERENCES solutions(id)
);

CREATE TABLE IF NOT EXISTS contributions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repository_id INTEGER,
    contribution_type TEXT NOT NULL,
    description TEXT NOT NULL,
    difficulty TEXT DEFAULT 'LOW',
    estimated_minutes INTEGER DEFAULT 15,
    status TEXT DEFAULT 'IDENTIFIED',
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(repository_id) REFERENCES repositories(id)
);

CREATE TABLE IF NOT EXISTS agent_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL UNIQUE,
    status TEXT DEFAULT 'RUNNING',
    repositories_scanned INTEGER DEFAULT 0,
    issues_found INTEGER DEFAULT 0,
    solutions_proposed INTEGER DEFAULT 0,
    changes_applied INTEGER DEFAULT 0,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS github_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repository_id INTEGER NOT NULL,
    action_type TEXT NOT NULL, -- BRANCH_CREATE, COMMIT, PULL_REQUEST
    branch_name TEXT,
    commit_sha TEXT,
    pr_number INTEGER,
    action_hash TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(repository_id) REFERENCES repositories(id)
);

CREATE TABLE IF NOT EXISTS ai_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation TEXT NOT NULL,
    repository_id INTEGER,
    model TEXT NOT NULL,
    input_hash TEXT NOT NULL,
    prompt_version TEXT DEFAULT '1.0',
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    estimated_cost REAL DEFAULT 0.0,
    success BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


def run_migrations(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()
    cursor.executescript(MIGRATION_SQL)
    conn.commit()
