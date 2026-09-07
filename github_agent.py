#!/usr/bin/env python3
"""
GitHub AI Agent — CLI Entry Point
A local-first maintainer for your GitHub profile and repositories.
"""
import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import argparse
import logging
from typing import Optional

from config import Config
from database import get_db
from agent import (
    RepositoryScanner,
    ProfileManager,
    Prioritizer,
    IssueManager,
    SolutionManager,
    ContributionManager,
    ApprovalManager,
    Reporter,
)
from github.repositories import RepositoryService
from github.client import GitHubClient

logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL.upper(), logging.INFO),
    format="[%(asctime)s] %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(Config.LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("github-agent")


def cmd_status(args):
    print("========================================")
    print(" GITHUB AI AGENT - SYSTEM STATUS")
    print("========================================")

    print(f"Database:        {Config.DB_PATH} ({'Exists' if Config.DB_PATH.exists() else 'Initialized'})")
    print(f"GitHub Username: {Config.GITHUB_USERNAME or '[Not configured in .env]'}")
    print(f"GitHub Token:    {'Configured (Active)' if Config.GITHUB_TOKEN else '[Missing GITHUB_TOKEN]'}")
    print(f"AI Provider:     {Config.AI_PROVIDER} ({Config.AI_MODEL})")
    print(f"AI Key:          {'Configured' if Config.AI_API_KEY else '[Heuristic fallback mode active]'}")
    print(f"Default Policy:  modify_source_code = FALSE (Strict Enforced)")
    print("========================================")


def cmd_profile(args):
    print("\nAnalyzing GitHub Profile...")
    mgr = ProfileManager()
    res = mgr.inspect_profile(args.username or Config.GITHUB_USERNAME)
    print(f"\nGitHub Profile Health: {res['profile_health_score']:.1f}/100")
    print(f"Username:              {res['username']}")
    print(f"Profile README:        {res['profile_readme']}")
    print(f"Bio:                   {res['bio']}")
    print(f"Website:               {res['website']}")
    if res["recommendations"]:
        print("\nRecommendations:")
        for r in res["recommendations"]:
            print(f"  • {r}")
    print("")


def cmd_ai_test(args):
    from ai.provider import AIProvider
    print("\n========================================")
    print(" GITHUB AI AGENT - AI HEALTH & DIAGNOSTIC")
    print("========================================")
    provider = AIProvider()
    print(f"Provider Configured: {provider.provider}")
    print(f"Target Model:        {provider.model}")
    print("Sending ping prompt to AI model...")

    res = provider.test_connection()
    if res["success"]:
        print("\n[+] STATUS:  ONLINE & OPERATIONAL")
        print(f"[+] Model:   {res['model']}")
        print(f"[+] Latency: {res['latency_ms']} ms")
        print(f"[+] Output:  \"{res['output']}\"")
        print("[+] Safety:  No-Source-Code Modification Filter ACTIVE")
    else:
        print("\n[-] STATUS:  OFFLINE / ERROR")
        print(f"[-] Error:   {res['error']}")
        print(f"[-] Fallback:{res['output']}")
    print("========================================\n")


def cmd_repos(args):
    print("\nRetrieving and ranking repositories...")
    service = RepositoryService()
    repos = service.list_repositories(args.username or Config.GITHUB_USERNAME)
    ranked = Prioritizer.rank_repositories(repos)

    print(f"\nTotal Repositories Found: {len(ranked)}")
    print("=" * 95)
    print(f"{'Priority':<10} {'Repository Name':<32} {'Stars':<7} {'Type':<9} {'Selection Criteria'}")
    print("=" * 95)
    for r in ranked[:25]:
        repo_type = "Fork" if r.get("fork") else ("Private" if r.get("private") else "Public")
        reasons_str = ", ".join(r.get("priority_reasons", [])[:3])
        print(f"{r.get('calculated_priority', 0):<10.1f} {r.get('full_name', '')[:31]:<32} {r.get('stargazers_count', 0):<7} {repo_type:<9} {reasons_str}")
    print("=" * 95)



def cmd_scan(args):
    repo_name = args.repo
    if not repo_name:
        print("Please provide a repository name (e.g., owner/repo).")
        return

    parts = repo_name.split("/")
    if len(parts) != 2:
        print("Invalid repository format. Must be owner/repo")
        return

    owner, name = parts
    print(f"\nScanning repository {owner}/{name}...")
    db = get_db()
    scanner = RepositoryScanner(db)

    # Ensure repository row in DB
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM repositories WHERE full_name = ?", (repo_name,))
        row = cursor.fetchone()
        if not row:
            cursor.execute(
                "INSERT INTO repositories (github_repo_id, full_name, name) VALUES (?, ?, ?)",
                (0, repo_name, name)
            )
            conn.commit()
            repo_id = cursor.lastrowid
        else:
            repo_id = row["id"]

    result = scanner.scan_repository(owner, name, repo_id)
    print(f"\nScan completed!")
    print(f"Health Score: {result.get('health_score', 0):.1f}/100")
    print(f"Summary: {result.get('summary', '')}")


def cmd_issues(args):
    issue_mgr = IssueManager()
    issues = issue_mgr.list_issues()
    print(f"\nTotal Logged Issues: {len(issues)}")
    print("-" * 80)
    for iss in issues:
        print(f"[{iss['category']}] [{iss['status']}] {iss['issue_type']}: {iss['description']} ({iss['affected_resource']})")
    print("-" * 80)


def cmd_solutions(args):
    sol_mgr = SolutionManager()
    solutions = sol_mgr.list_solutions(args.status)
    print(f"\nProposed Solutions ({len(solutions)}):")
    print("-" * 80)
    for sol in solutions:
        print(f"ID #{sol['id']} | [{sol['status']}] {sol['title']} -> {sol['target_file']} (Risk: {sol['risk_level']})")
    print("-" * 80)


def cmd_approve(args):
    sol_mgr = SolutionManager()
    solutions = sol_mgr.list_solutions(status="PENDING")
    if not solutions:
        print("No pending solutions to approve.")
        return

    target = None
    if args.solution_id:
        target = next((s for s in solutions if s["id"] == args.solution_id), None)
        if not target:
            print(f"Solution ID #{args.solution_id} not found in PENDING list.")
            return
    else:
        target = solutions[0]

    approver = ApprovalManager()
    decision = approver.prompt_user(target, f"Repo #{target['repository_id']}")
    print(f"Decision recorded: {decision}")


def cmd_contributions(args):
    contrib_mgr = ContributionManager()
    today = contrib_mgr.get_todays_opportunity()

    print("\n========================================")
    print("TODAY'S GITHUB OPPORTUNITY")
    print("========================================")
    if today:
        print(f"Repository:               {today.get('repo_name', 'Configured Repository')}")
        print(f"Recommended contribution: {today.get('description')}")
        print(f"Difficulty:               {today.get('difficulty', 'Low')}")
        print(f"Estimated time:           {today.get('estimated_minutes', 15)} minutes")
        print(f"Requires approval:        YES")
    else:
        print("No pending contribution opportunities found in recent scans.")
        print("Run 'python github_agent.py run' to scan repositories and discover useful opportunities.")
    print("========================================\n")


def cmd_run(args):
    from agent.workflow import AutomatedWorkflow

    workflow = AutomatedWorkflow()
    workflow.run(
        limit=args.limit or Config.get_repositories_per_run(),
        auto_approve=getattr(args, "yes", False),
        apply_to_github=getattr(args, "apply", False),
        target_repo=getattr(args, "repo", None),
    )


def main():
    parser = argparse.ArgumentParser(
        description="GitHub AI Agent: Maintain and improve your GitHub profile and repositories."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    subparsers.add_parser("status", help="Show system configuration and readiness")

    profile_parser = subparsers.add_parser("profile", help="Analyze GitHub profile")
    profile_parser.add_argument("--username", help="Target GitHub username")

    repos_parser = subparsers.add_parser("repos", help="List and rank repositories")
    repos_parser.add_argument("--username", help="Target GitHub username")

    scan_parser = subparsers.add_parser("scan", help="Scan a specific repository")
    scan_parser.add_argument("repo", help="Repository in owner/name format")

    issues_parser = subparsers.add_parser("issues", help="List detected issues")
    issues_parser.add_argument("--repo", help="Filter by repository")

    solutions_parser = subparsers.add_parser("solutions", help="List proposed solutions")
    solutions_parser.add_argument("--status", choices=["PENDING", "APPROVED", "APPLIED", "REJECTED"], help="Filter by status")

    approve_parser = subparsers.add_parser("approve", help="Approve or reject proposed solutions")
    approve_parser.add_argument("solution_id", nargs="?", type=int, help="Solution ID to approve")

    subparsers.add_parser("contributions", help="View legitimate contribution opportunities")

    subparsers.add_parser("ai-test", help="Test AI model connectivity, latency, and response")
    subparsers.add_parser("ai-health", help="Alias for ai-test")

    run_parser = subparsers.add_parser("run", help="Run the full automated end-to-end pipeline")
    run_parser.add_argument("--limit", type=int, default=5, help="Number of repositories to scan (default: 5)")
    run_parser.add_argument("--repo", help="Target specific repository (e.g. owner/repo)")
    run_parser.add_argument("--apply", action="store_true", help="Apply approved fixes to GitHub (create branch, commit, PR)")
    run_parser.add_argument("--yes", "-y", action="store_true", help="Auto-approve all safe fixes in unattended mode")

    auto_parser = subparsers.add_parser("auto", help="Alias for full automated workflow")
    auto_parser.add_argument("--limit", type=int, default=5, help="Number of repositories to scan (default: 5)")
    auto_parser.add_argument("--repo", help="Target specific repository (e.g. owner/repo)")
    auto_parser.add_argument("--apply", action="store_true", help="Apply approved fixes to GitHub (create branch, commit, PR)")
    auto_parser.add_argument("--yes", "-y", action="store_true", help="Auto-approve all safe fixes in unattended mode")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    dispatch = {
        "status": cmd_status,
        "profile": cmd_profile,
        "repos": cmd_repos,
        "scan": cmd_scan,
        "issues": cmd_issues,
        "solutions": cmd_solutions,
        "approve": cmd_approve,
        "contributions": cmd_contributions,
        "ai-test": cmd_ai_test,
        "ai-health": cmd_ai_test,
        "run": cmd_run,
        "auto": cmd_run,
    }


    handler = dispatch.get(args.command)
    if handler:
        handler(args)


if __name__ == "__main__":
    main()

