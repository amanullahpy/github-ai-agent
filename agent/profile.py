from typing import Dict, Any, Optional
from database import Database, get_db
from database.models import GitHubProfile
from github.repositories import RepositoryService


class ProfileManager:
    def __init__(self, db: Optional[Database] = None, repo_service: Optional[RepositoryService] = None):
        self.db = db or get_db()
        self.repo_service = repo_service or RepositoryService()

    def inspect_profile(self, username: Optional[str] = None) -> Dict[str, Any]:
        data = self.repo_service.get_user_profile(username)
        user_login = data.get("login", "")

        # Check special repository for profile README: username/username
        readme_present = False
        if user_login:
            readme_content = self.repo_service.get_file_content(user_login, user_login, "README.md")
            if readme_content:
                readme_present = True

        score = 0.0
        recommendations = []

        if data.get("name"):
            score += 15.0
        else:
            recommendations.append("Add full name to GitHub profile.")

        if data.get("bio"):
            score += 20.0
        else:
            recommendations.append("Add a concise professional bio with tech stack and focus.")

        if data.get("blog") or data.get("html_url"):
            score += 15.0
        else:
            recommendations.append("Link personal website or portfolio.")

        if readme_present:
            score += 30.0
        else:
            recommendations.append(f"Create a profile README repository ({user_login}/{user_login}).")

        if data.get("public_repos", 0) > 0:
            score += 20.0

        profile_obj = GitHubProfile(
            username=user_login,
            name=data.get("name"),
            bio=data.get("bio"),
            website=data.get("blog"),
            public_repos=data.get("public_repos", 0),
            followers=data.get("followers", 0),
            following=data.get("following", 0),
            profile_readme_present=readme_present,
            profile_health_score=score,
        )

        with self.db.get_connection() as conn:
            conn.execute(
                """
                INSERT INTO github_profile
                (username, name, bio, website, public_repos, followers, following, profile_readme_present, profile_health_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    profile_obj.username,
                    profile_obj.name,
                    profile_obj.bio,
                    profile_obj.website,
                    profile_obj.public_repos,
                    profile_obj.followers,
                    profile_obj.following,
                    int(profile_obj.profile_readme_present),
                    profile_obj.profile_health_score,
                )
            )
            conn.commit()

        return {
            "username": user_login,
            "profile_health_score": score,
            "profile_readme": "Good" if readme_present else "Missing",
            "bio": "Good" if data.get("bio") else "Needs improvement",
            "website": "Configured" if data.get("blog") else "Missing",
            "recommendations": recommendations,
        }
