from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple

PORTFOLIO_KEYWORDS = [
    "portfolio", "showcase", "platform", "hub", "tool", "app", "lab", "api",
    "fullstack", "ai", "game", "games", "bot", "agent", "service", "assignment"
]


class Prioritizer:
    @staticmethod
    def calculate_priority_with_reasons(
        repo: Dict[str, Any],
        last_scanned_at: Any = None
    ) -> Tuple[float, List[str]]:
        score = 50.0
        reasons = []

        name_lower = repo.get("name", "").lower()
        desc_lower = (repo.get("description") or "").lower()

        # 1. Portfolio & Showcase Relevance (+15)
        matched_kw = [kw for kw in PORTFOLIO_KEYWORDS if kw in name_lower or kw in desc_lower]
        if matched_kw:
            score += 15.0
            reasons.append(f"Portfolio keyword ({matched_kw[0]})")

        # 2. Public vs Private
        is_private = repo.get("private", False)
        if not is_private:
            score += 10.0
            reasons.append("Public visibility")
        else:
            score += 5.0
            reasons.append("Private maintenance")

        # 3. Social Proof & Stars
        stars = repo.get("stargazers_count", 0)
        forks = repo.get("forks_count", 0)
        if stars >= 5:
            score += 15.0
            reasons.append(f"High stars ({stars}★)")
        elif stars > 0:
            score += 5.0
            reasons.append(f"Has stars ({stars}★)")
        if forks > 0:
            score += 5.0

        # 4. Recent Activity
        updated_at = repo.get("updated_at")
        if updated_at:
            try:
                # ISO date string e.g. 2026-09-07T...
                dt = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
                days_since_update = (datetime.now(timezone.utc) - dt).days
                if days_since_update < 30:
                    score += 10.0
                    reasons.append("Active recently (<30d)")
            except Exception:
                pass

        # 5. Maintenance / Scan Freshness
        if not last_scanned_at:
            score += 20.0
            reasons.append("Never scanned before")
        else:
            score += 5.0

        # 6. Documentation Quick-Win Opportunities
        if not repo.get("description"):
            score += 5.0
            reasons.append("Missing description (Quick fix)")
        if not repo.get("topics"):
            score += 5.0
            reasons.append("Missing topics (Quick fix)")

        # 7. Deprioritizations
        if repo.get("fork", False):
            score -= 30.0
            reasons.append("Fork repository (-30)")
        if repo.get("archived", False):
            score -= 40.0
            reasons.append("Archived repository (-40)")

        final_score = max(0.0, min(100.0, score))
        return final_score, reasons

    @staticmethod
    def calculate_priority(repo: Dict[str, Any], last_scanned_days: int = 30) -> float:
        score, _ = Prioritizer.calculate_priority_with_reasons(repo)
        return score

    @staticmethod
    def rank_repositories(repos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        for r in repos:
            score, reasons = Prioritizer.calculate_priority_with_reasons(r)
            r["calculated_priority"] = score
            r["priority_reasons"] = reasons
        return sorted(repos, key=lambda x: x["calculated_priority"], reverse=True)
