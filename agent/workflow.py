import logging
from typing import Dict, Any, List, Optional
from config import Config
from database import Database, get_db
from agent.profile import ProfileManager
from agent.prioritizer import Prioritizer
from agent.scanner import RepositoryScanner
from agent.issue_manager import IssueManager
from agent.solution_manager import SolutionManager
from agent.solution_generator import SolutionGenerator
from agent.contribution import ContributionManager
from agent.approval import ApprovalManager
from agent.reporter import Reporter
from github.repositories import RepositoryService
from github.branches import BranchService
from github.commits import CommitService
from github.pull_requests import PullRequestService

logger = logging.getLogger("github-agent.workflow")


class AutomatedWorkflow:
    def __init__(self, db: Optional[Database] = None):
        self.db = db or get_db()
        self.profile_mgr = ProfileManager(self.db)
        self.repo_service = RepositoryService()
        self.scanner = RepositoryScanner(self.db, self.repo_service)
        self.issue_mgr = IssueManager(self.db)
        self.solution_mgr = SolutionManager(self.db)
        self.solution_gen = SolutionGenerator(self.db, self.solution_mgr)
        self.contrib_mgr = ContributionManager(self.db)
        self.approval_mgr = ApprovalManager(self.db)
        self.branch_service = BranchService()
        self.commit_service = CommitService()
        self.pr_service = PullRequestService()

    def run(
        self,
        limit: int = 2,
        auto_approve: bool = False,
        apply_to_github: bool = False,
        target_repo: Optional[str] = None
    ) -> Dict[str, Any]:
        print("\n" + "=" * 60)
        print("  [*] GITHUB AI AGENT - FULL AUTOMATED RUN")
        print("=" * 60)

        # 1. Profile Inspection
        print("\n[1/6] Inspecting GitHub Profile...")
        profile_res = self.profile_mgr.inspect_profile(Config.GITHUB_USERNAME)
        print(f"      Profile: @{profile_res['username']} | Health: {profile_res['profile_health_score']:.1f}/100")

        # 2. Repository Discovery (Public & Private)
        print("\n[2/6] Discovering repositories (Public & Private)...")
        all_repos = self.repo_service.list_repositories(Config.GITHUB_USERNAME)
        private_count = sum(1 for r in all_repos if r.get("private"))
        public_count = len(all_repos) - private_count
        print(f"      Total Discovered: {len(all_repos)} ({public_count} Public, {private_count} Private)")


        # Filter and Rank
        if target_repo:
            selected_repos = [r for r in all_repos if r.get("full_name", "").lower() == target_repo.lower()]
            if not selected_repos:
                # If not found in user repos, try direct fetch
                parts = target_repo.split("/")
                if len(parts) == 2:
                    repo_obj = self.repo_service.get_repository(parts[0], parts[1])
                    if repo_obj and "id" in repo_obj:
                        selected_repos = [repo_obj]
        else:
            ranked = Prioritizer.rank_repositories(all_repos)
            selected_repos = [r for r in ranked if not r.get("fork") and not r.get("archived")][:limit]

        print(f"      Selected for scanning: {len(selected_repos)} repositories")

        total_issues_found = 0
        total_solutions_prepared = 0
        total_prs_created = 0

        # 3. Process Each Selected Repository
        for idx, repo in enumerate(selected_repos, 1):
            full_name = repo.get("full_name", "")
            owner, name = full_name.split("/")
            repo_type = "Private" if repo.get("private") else "Public"
            default_branch = repo.get("default_branch", "main")

            print(f"\n[{idx}/{len(selected_repos)}] [>] Processing {full_name} ({repo_type})...")

            # Ensure repo registered in local DB
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM repositories WHERE full_name = ?", (full_name,))
                row = cursor.fetchone()
                if not row:
                    cursor.execute(
                        """
                        INSERT INTO repositories (github_repo_id, full_name, name, description, homepage, default_branch, is_private)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            repo.get("id", 0),
                            full_name,
                            name,
                            repo.get("description"),
                            repo.get("homepage"),
                            default_branch,
                            int(repo.get("private", False)),
                        )
                    )
                    conn.commit()
                    repo_id = cursor.lastrowid
                else:
                    repo_id = row["id"]

            # Scan
            scan_res = self.scanner.scan_repository(owner, name, repo_id)
            health = scan_res.get("health_score", 0)
            print(f"      Health Score: {health:.1f}/100")

            # Issues
            issues = self.issue_mgr.list_issues(repo_id)
            repo_issues = [i for i in issues if i["category"] == "REPOSITORY"]
            code_issues = [i for i in issues if i["category"] == "CODE"]
            total_issues_found += len(issues)

            print(f"      Issues Detected: {len(repo_issues)} Repository-level (FIXABLE), {len(code_issues)} Code-level (DO NOT MODIFY)")

            # Generate Solutions for fixable issues
            readme_content = self.repo_service.get_file_content(owner, name, "README.md") or ""
            prepared_solutions = []

            for r_iss in repo_issues:
                try:
                    sol = self.solution_gen.generate_solution_for_issue(
                        repo_id, full_name, r_iss, readme_content, repo_metadata=repo
                    )
                    if sol:
                        prepared_solutions.append(sol)
                        total_solutions_prepared += 1
                except Exception as e:
                    logger.warning(f"Could not generate solution for issue {r_iss['id']}: {e}")

            print(f"      Solutions Prepared: {len(prepared_solutions)}")

            # Opportunities
            opps = self.contrib_mgr.identify_opportunities(repo_id, full_name)

            # Retrieve Feature Suggestions from DB
            sug_list = []
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM feature_suggestions WHERE repository_id = ?", (repo_id,))
                sug_list = [dict(s) for s in cursor.fetchall()]

            # Write Reports
            bundle_dir = Reporter.write_reports_bundle(
                full_name,
                scan_res,
                repo_issues,
                code_issues,
                [s.__dict__ for s in prepared_solutions],
                sug_list,
            )
            print(f"      Reports generated at: {bundle_dir}")


            # Apply Solutions to GitHub if requested
            if apply_to_github and prepared_solutions:
                print(f"\n      [*] Applying approved fixes to GitHub...")
                for sol in prepared_solutions:
                    decision = "APPROVE" if auto_approve else self.approval_mgr.prompt_user(sol.__dict__, full_name)
                    if decision == "APPROVE":
                        try:
                            # 1. Create safe branch
                            branch_suffix = sol.target_file.replace("/", "-").replace(".", "-").lower()
                            branch_name = f"github-agent/fix-{branch_suffix}"
                            print(f"      Creating branch: {branch_name}...")
                            self.branch_service.create_safe_branch(owner, name, branch_name, base_branch=default_branch)

                            # 2. Commit file
                            print(f"      Committing fix for {sol.target_file}...")
                            self.commit_service.create_or_update_file(
                                owner=owner,
                                repo=name,
                                path=sol.target_file,
                                content=sol.proposed_change,
                                message=f"improve {sol.target_file}",
                                branch=branch_name,
                            )

                            # 3. Create PR
                            print(f"      Opening Pull Request...")
                            pr_res = self.pr_service.create_pull_request(
                                owner=owner,
                                repo=name,
                                title=f"chore(github-agent): {sol.title}",
                                head=branch_name,
                                base=default_branch,
                                body=f"Automated quality improvement: {sol.title}\n\nTarget: `{sol.target_file}`",
                            )
                            pr_url = pr_res.get("html_url", "Created")
                            print(f"      [+] Pull Request created: {pr_url}")
                            total_prs_created += 1

                            # Update solution status
                            with self.db.get_connection() as conn:
                                conn.execute("UPDATE solutions SET status = 'APPLIED' WHERE id = ?", (sol.id,))
                                conn.commit()

                        except Exception as e:
                            logger.error(f"Failed to apply solution {sol.id} to {full_name}: {e}")
                            print(f"      [-] Failed to apply to GitHub: {e}")

        print("\n" + "=" * 60)
        print("  [*] AUTOMATED PIPELINE COMPLETE")
        print("=" * 60)

        print(f"  Repositories Processed: {len(selected_repos)}")
        print(f"  Total Issues Logged:    {total_issues_found}")
        print(f"  Solutions Prepared:     {total_solutions_prepared}")
        print(f"  Pull Requests Created:  {total_prs_created}")
        print(f"  Local Reports Updated:  reports/")
        print("=" * 60 + "\n")

        return {
            "repositories_processed": len(selected_repos),
            "issues_logged": total_issues_found,
            "solutions_prepared": total_solutions_prepared,
            "prs_created": total_prs_created,
        }
