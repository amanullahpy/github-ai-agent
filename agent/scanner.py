import hashlib
import json
import logging
from typing import Dict, Any, Optional
from database import Database, get_db
from database.models import RepositoryScan, FeatureSuggestion
from github.repositories import RepositoryService
from .issue_manager import IssueManager
from ai.provider import AIProvider
from ai.prompts import FEATURE_SUGGESTIONS_PROMPT

logger = logging.getLogger(__name__)


class RepositoryScanner:
    def __init__(
        self,
        db: Optional[Database] = None,
        repo_service: Optional[RepositoryService] = None,
        issue_manager: Optional[IssueManager] = None,
        ai_provider: Optional[AIProvider] = None,
    ):
        self.db = db or get_db()
        self.repo_service = repo_service or RepositoryService()
        self.issue_manager = issue_manager or IssueManager(self.db)
        self.ai = ai_provider or AIProvider()


    @staticmethod
    def compute_scan_hash(metadata: Dict[str, Any], readme: str, github_files: list) -> str:
        payload = {
            "name": metadata.get("name"),
            "desc": metadata.get("description"),
            "topics": metadata.get("topics"),
            "readme_hash": hashlib.sha256(readme.encode("utf-8")).hexdigest() if readme else "",
            "github_files": sorted(github_files),
        }
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()

    def scan_repository(self, owner: str, repo_name: str, repo_id_db: int) -> Dict[str, Any]:
        metadata = self.repo_service.get_repository(owner, repo_name)
        readme = self.repo_service.get_file_content(owner, repo_name, "README.md") or ""

        github_dir = self.repo_service.get_directory_contents(owner, repo_name, ".github")
        github_files = [item.get("name", "") for item in github_dir if isinstance(item, dict)]

        scan_hash = self.compute_scan_hash(metadata, readme, github_files)

        # Idempotency check: Skip expensive analysis if scan_hash matches previous scan
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM repository_scans WHERE scan_hash = ?", (scan_hash,))
            existing = cursor.fetchone()
            if existing:
                logger.info(f"Repository {owner}/{repo_name} unchanged (scan_hash matches). Reusing cached scan.")
                return dict(existing)

        # Dimension Scoring
        doc_score = 0.0
        meta_score = 0.0
        standards_score = 0.0
        dx_score = 0.0
        discover_score = 0.0
        maint_score = 0.0
        pres_score = 0.0

        readme_lower = readme.lower()

        # 1. Documentation (20%)
        if readme:
            doc_score += 8.0
            if "installation" in readme_lower or "setup" in readme_lower or "getting started" in readme_lower:
                doc_score += 4.0
            else:
                self.issue_manager.record_issue(
                    repo_id_db, f"{owner}/{repo_name}", "MISSING_README_INSTALLATION",
                    "README is missing installation instructions.", "README.md", "LOW"
                )

            if "usage" in readme_lower or "quickstart" in readme_lower:
                doc_score += 4.0
            else:
                self.issue_manager.record_issue(
                    repo_id_db, f"{owner}/{repo_name}", "MISSING_README_USAGE",
                    "README is missing usage instructions.", "README.md", "LOW"
                )

            if "license" in readme_lower:
                doc_score += 4.0

        # 2. Metadata (10%)
        if metadata.get("description"):
            meta_score += 5.0
        else:
            self.issue_manager.record_issue(
                repo_id_db, f"{owner}/{repo_name}", "MISSING_DESCRIPTION",
                "Repository description is empty.", "metadata", "LOW"
            )

        if metadata.get("topics"):
            meta_score += 5.0
        else:
            self.issue_manager.record_issue(
                repo_id_db, f"{owner}/{repo_name}", "MISSING_TOPICS",
                "Relevant repository topics are missing.", "metadata", "LOW"
            )

        # 3. Standards (15%)
        license_info = metadata.get("license")
        if license_info:
            standards_score += 7.5
        else:
            self.issue_manager.record_issue(
                repo_id_db, f"{owner}/{repo_name}", "MISSING_LICENSE",
                "Repository is missing an open source license file.", "LICENSE", "MEDIUM"
            )

        if "workflows" in github_files or any("action" in f for f in github_files):
            standards_score += 7.5

        # 4. Developer Experience (15%)
        if any("issue_template" in f.lower() for f in github_files):
            dx_score += 7.5
        else:
            self.issue_manager.record_issue(
                repo_id_db, f"{owner}/{repo_name}", "MISSING_ISSUE_TEMPLATE",
                "No issue template exists.", ".github/ISSUE_TEMPLATE", "LOW"
            )

        if any("pull_request_template" in f.lower() for f in github_files):
            dx_score += 7.5
        else:
            self.issue_manager.record_issue(
                repo_id_db, f"{owner}/{repo_name}", "MISSING_PR_TEMPLATE",
                "No pull request template exists.", ".github/PULL_REQUEST_TEMPLATE", "LOW"
            )

        # 5. Discoverability (15%)
        if metadata.get("homepage"):
            discover_score += 8.0
        else:
            self.issue_manager.record_issue(
                repo_id_db, f"{owner}/{repo_name}", "MISSING_HOMEPAGE",
                "No demo URL / homepage is configured.", "metadata", "LOW"
            )
        if len(metadata.get("topics", [])) >= 3:
            discover_score += 7.0

        # 6. Maintenance (15%)
        if not metadata.get("archived", False):
            maint_score += 15.0

        # 7. Presentation (10%)
        if "![" in readme or "<img" in readme:
            pres_score += 10.0
        else:
            self.issue_manager.record_issue(
                repo_id_db, f"{owner}/{repo_name}", "MISSING_README_SCREENSHOTS",
                "README lacks screenshots or architectural visuals.", "README.md", "LOW"
            )

        total_health = doc_score + meta_score + standards_score + dx_score + discover_score + maint_score + pres_score
        summary_text = (
            f"Health Score: {total_health:.1f}/100. "
            f"Doc: {doc_score}/20, Meta: {meta_score}/10, Standards: {standards_score}/15, "
            f"DX: {dx_score}/15, Discoverability: {discover_score}/15, "
            f"Maintenance: {maint_score}/15, Presentation: {pres_score}/10."
        )

        scan_result = RepositoryScan(
            repository_id=repo_id_db,
            scan_hash=scan_hash,
            health_score=total_health,
            documentation_score=doc_score,
            metadata_score=meta_score,
            standards_score=standards_score,
            dx_score=dx_score,
            discoverability_score=discover_score,
            maintenance_score=maint_score,
            presentation_score=pres_score,
            summary=summary_text,
        )

        with self.db.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO repository_scans
                (repository_id, scan_hash, health_score, documentation_score, metadata_score, standards_score,
                 dx_score, discoverability_score, maintenance_score, presentation_score, summary)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    scan_result.repository_id,
                    scan_result.scan_hash,
                    scan_result.health_score,
                    scan_result.documentation_score,
                    scan_result.metadata_score,
                    scan_result.standards_score,
                    scan_result.dx_score,
                    scan_result.discoverability_score,
                    scan_result.maintenance_score,
                    scan_result.presentation_score,
                    scan_result.summary,
                )
            )
            conn.commit()

        # Generate AI Feature Suggestions if not already present
        self._generate_feature_suggestions(owner, repo_name, repo_id_db, metadata)


        return {
            "repository_id": repo_id_db,
            "scan_hash": scan_hash,
            "health_score": total_health,
            "documentation_score": doc_score,
            "metadata_score": meta_score,
            "standards_score": standards_score,
            "dx_score": dx_score,
            "discoverability_score": discover_score,
            "maintenance_score": maint_score,
            "presentation_score": pres_score,
            "summary": summary_text,
        }

    def _generate_feature_suggestions(
        self,
        owner: str,
        repo_name: str,
        repo_id: int,
        metadata: Dict[str, Any]
    ) -> None:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) as cnt FROM feature_suggestions WHERE repository_id = ?", (repo_id,))
            if cursor.fetchone()["cnt"] > 0:
                return

        prompt = FEATURE_SUGGESTIONS_PROMPT.format(
            repo_name=f"{owner}/{repo_name}",
            description=metadata.get("description") or "No description provided",
            tech_stack=metadata.get("language") or "General Software",
            details=f"Stars: {metadata.get('stargazers_count', 0)}, Forks: {metadata.get('forks_count', 0)}",
        )

        try:
            print(f"      [AI] Generating feature suggestions for {owner}/{repo_name} using {self.ai.model}...")
            ai_res = self.ai.generate(prompt, operation="feature_suggestions", repository_id=repo_id)
            if ai_res and len(ai_res) > 50:
                sug_hash = hashlib.sha256(f"{repo_id}:suggestions:{ai_res[:100]}".encode("utf-8")).hexdigest()
                with self.db.get_connection() as conn:
                    conn.execute(
                        """
                        INSERT OR IGNORE INTO feature_suggestions
                        (repository_id, title, description, priority, expected_benefit, suggested_implementation, suggestion_hash)
                        VALUES (?, ?, ?, 'MEDIUM', ?, ?, ?)
                        """,
                        (
                            repo_id,
                            f"AI Feature Recommendations for {repo_name}",
                            ai_res,
                            "Elevate project presentation & functionality",
                            ai_res,
                            sug_hash,
                        )
                    )
                    conn.commit()
        except Exception as e:
            logger.warning(f"Could not generate feature suggestions: {e}")

