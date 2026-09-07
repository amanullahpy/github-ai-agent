from pathlib import Path
from typing import Dict, Any, List, Optional
from config import REPORTS_DIR


class Reporter:
    @staticmethod
    def generate_scan_report(repo_name: str, scan_data: Dict[str, Any]) -> str:
        content = f"""# GitHub Agent Scan Report: {repo_name}

Repository Health: {scan_data.get('health_score', 0):.1f}/100

## Scores

- Documentation: {scan_data.get('documentation_score', 0):.1f}/20
- Metadata: {scan_data.get('metadata_score', 0):.1f}/10
- GitHub Standards: {scan_data.get('standards_score', 0):.1f}/15
- Developer Experience: {scan_data.get('dx_score', 0):.1f}/15
- Discoverability: {scan_data.get('discoverability_score', 0):.1f}/15
- Maintenance: {scan_data.get('maintenance_score', 0):.1f}/15
- Presentation: {scan_data.get('presentation_score', 0):.1f}/10

## Summary

{scan_data.get('summary', 'Scan completed successfully.')}
"""
        return content

    @staticmethod
    def generate_issues_report(repo_name: str, repo_issues: List[Dict[str, Any]], code_issues: List[Dict[str, Any]]) -> str:
        lines = [f"# Repository Issues: {repo_name}\n"]

        lines.append("## Repository-Level Issues (FIXABLE)\n")
        if not repo_issues:
            lines.append("No open repository-level issues found.\n")
        else:
            for i, iss in enumerate(repo_issues, 1):
                lines.append(f"### Issue #{i}: {iss.get('issue_type')}")
                lines.append(f"- **Problem**: {iss.get('description')}")
                lines.append(f"- **Resource**: `{iss.get('affected_resource')}`")
                lines.append(f"- **Severity**: {iss.get('severity')}")
                lines.append(f"- **Status**: FIXABLE\n")

        lines.append("## Code-Level Issues (DO NOT MODIFY)\n")
        if not code_issues:
            lines.append("No code-level architectural/quality issues logged.\n")
        else:
            for i, iss in enumerate(code_issues, 1):
                lines.append(f"### Issue #{i}: {iss.get('issue_type')}")
                lines.append(f"- **File**: `{iss.get('affected_resource')}`")
                lines.append(f"- **Description**: {iss.get('description')}")
                lines.append(f"- **Severity**: {iss.get('severity')}")
                lines.append(f"- **Agent Action**: DO NOT MODIFY (Report only)\n")

        return "\n".join(lines)

    @staticmethod
    def generate_solutions_report(repo_name: str, solutions: List[Dict[str, Any]]) -> str:
        lines = [f"# Proposed Solutions: {repo_name}\n"]
        if not solutions:
            lines.append("No active solutions pending or prepared.\n")
        else:
            for i, sol in enumerate(solutions, 1):
                lines.append(f"## Solution #{i}: {sol.get('title')}")
                lines.append(f"- **Target File**: `{sol.get('target_file')}`")
                lines.append(f"- **Risk**: {sol.get('risk_level', 'LOW')}")
                lines.append(f"- **Status**: {sol.get('status', 'PENDING')}")
                lines.append(f"- **Proposed Change**:\n```\n{sol.get('proposed_change', '')}\n```\n")
        return "\n".join(lines)

    @staticmethod
    def generate_feature_suggestions(repo_name: str, suggestions: List[Dict[str, Any]]) -> str:
        lines = [f"# Feature Suggestions: {repo_name}\n"]
        if not suggestions:
            lines.append("No feature suggestions at this time.\n")
        else:
            for i, sug in enumerate(suggestions, 1):
                lines.append(f"## {i}. {sug.get('title')}")
                lines.append(f"- **Priority**: {sug.get('priority', 'MEDIUM')}")
                lines.append(f"- **Expected Benefit**: {sug.get('expected_benefit')}")
                lines.append(f"- **Suggested Implementation**: {sug.get('suggested_implementation')}")
                lines.append(f"- **Status**: SUGGESTED\n")
        return "\n".join(lines)

    @classmethod
    def write_reports_bundle(
        cls,
        repo_name: str,
        scan_data: Dict[str, Any],
        repo_issues: List[Dict[str, Any]],
        code_issues: List[Dict[str, Any]],
        solutions: List[Dict[str, Any]],
        suggestions: List[Dict[str, Any]],
        output_dir: Optional[Path] = None
    ) -> Path:
        out_dir = (output_dir or REPORTS_DIR) / repo_name.replace("/", "_")
        out_dir.mkdir(parents=True, exist_ok=True)

        (out_dir / "scan-report.md").write_text(cls.generate_scan_report(repo_name, scan_data), encoding="utf-8")
        (out_dir / "issues.md").write_text(cls.generate_issues_report(repo_name, repo_issues, code_issues), encoding="utf-8")
        (out_dir / "solutions.md").write_text(cls.generate_solutions_report(repo_name, solutions), encoding="utf-8")
        (out_dir / "feature-suggestions.md").write_text(cls.generate_feature_suggestions(repo_name, suggestions), encoding="utf-8")

        return out_dir
