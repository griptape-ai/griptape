"""
Code Proposer Module

Manages GitHub-integrated code change proposals from leadership bots.
Analyzes codebase, generates proposals, creates pull requests, and integrates
with Supabase for Denauld Brown's approval workflow.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class CodeChangeProposal:
    """Represents a code change proposal."""

    bot_id: str
    file_path: str
    change_description: str
    rationale: str
    impact_analysis: dict[str, Any]
    code_diff: str | None = None
    risk_level: str = "medium"  # low, medium, high
    estimated_impact: str = "moderate"  # minimal, moderate, significant, major
    testing_requirements: list[str] | None = None
    created_at: datetime | None = None

    def __post_init__(self) -> None:
        """Set created_at if not provided."""
        if self.created_at is None:
            self.created_at = datetime.now(UTC)
        if self.testing_requirements is None:
            self.testing_requirements = []


@dataclass
class PullRequestResult:
    """Result of creating a pull request."""

    pr_number: int
    pr_url: str
    branch_name: str
    proposal_id: str
    status: str  # created, pending_review, approved, rejected
    created_at: datetime


class CodeProposer:
    """
    Manages code change proposals with GitHub integration.

    This class enables leadership bots to analyze the codebase, propose changes,
    create GitHub pull requests, and integrate with Supabase for approval tracking.

    Attributes:
        bot_id: Unique identifier for the proposing bot
        github_token: GitHub Personal Access Token (from env)
        repo_name: Repository name (e.g., "AnalyzeMyTeamHQ/analyzemyteam-griptape-core")
        base_branch: Base branch for PRs (default: "main")

    Example:
        >>> proposer = CodeProposer(bot_id="rachel_foster")
        >>> proposal = proposer.propose_change(
        ...     file_path="griptape/engines/query_engine.py",
        ...     change_description="Optimize query caching",
        ...     rationale="Reduce API latency by 40%"
        ... )
        >>> pr_result = proposer.create_pull_request(proposal)
        >>> print(f"PR created: {pr_result.pr_url}")
    """

    def __init__(
        self,
        bot_id: str,
        github_token: str | None = None,
        repo_name: str = "AnalyzeMyTeamHQ/analyzemyteam-griptape-core",
        base_branch: str = "main",
    ) -> None:
        """
        Initialize CodeProposer.

        Args:
            bot_id: Unique identifier for the bot
            github_token: GitHub PAT (defaults to GITHUB_PAT env var)
            repo_name: Full repository name
            base_branch: Base branch for PRs
        """
        self.bot_id = bot_id
        self.repo_name = repo_name
        self.base_branch = base_branch
        self.github_token = github_token or os.getenv("GITHUB_PAT")

        if not self.github_token:
            logger.warning("No GitHub token provided - GitHub operations will fail")

        logger.info(f"CodeProposer initialized for {bot_id} targeting {repo_name}")

    def analyze_codebase(self, file_path: str | Path) -> dict[str, Any]:
        """
        Analyze a file in the codebase for potential improvements.

        Args:
            file_path: Path to the file to analyze

        Returns:
            Dictionary containing analysis results

        Example:
            >>> analysis = proposer.analyze_codebase("griptape/engines/query_engine.py")
            >>> print(analysis['complexity_score'])
        """
        from pathlib import Path

        file_path = Path(file_path)

        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return {"error": "File not found", "exists": False}

        try:
            content = file_path.read_text(encoding="utf-8")
            lines_of_code = len(content.splitlines())

            analysis = {
                "file_path": str(file_path),
                "exists": True,
                "lines_of_code": lines_of_code,
                "file_size_bytes": file_path.stat().st_size,
                "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime, tz=UTC),
                "complexity_score": self._calculate_complexity(content),
                "improvement_opportunities": self._identify_improvements(content),
            }

            logger.info(f"Analyzed {file_path}: {lines_of_code} LOC, complexity {analysis['complexity_score']}")
            return analysis

        except Exception as e:
            logger.exception(f"Error analyzing {file_path}: {e}")
            return {"error": str(e), "exists": True}

    def _calculate_complexity(self, content: str) -> int:
        """
        Calculate rough complexity score for code.

        Args:
            content: File content

        Returns:
            Complexity score (1-10)
        """
        # Simple heuristic based on nesting, functions, classes
        lines = content.splitlines()
        complexity = 1

        for line in lines:
            stripped = line.strip()
            if stripped.startswith(("def ", "class ", "async def ")):
                complexity += 1
            if stripped.startswith(("if ", "for ", "while ", "try:", "except")):
                complexity += 0.5

        # Normalize to 1-10 scale
        normalized = min(10, max(1, int(complexity / 10)))
        return normalized

    def _identify_improvements(self, content: str) -> list[str]:
        """
        Identify potential improvement opportunities.

        Args:
            content: File content

        Returns:
            List of improvement suggestions
        """
        improvements = []

        # Check for common patterns
        if "# TODO" in content or "# FIXME" in content:
            improvements.append("Contains TODO/FIXME comments")

        if content.count("try:") > 5:
            improvements.append("High exception handling - consider consolidation")

        if len(content.splitlines()) > 500:
            improvements.append("Large file - consider refactoring into modules")

        if "import *" in content:
            improvements.append("Contains wildcard imports - specify explicit imports")

        return improvements

    def propose_change(
        self,
        file_path: str | Path,
        change_description: str,
        rationale: str,
        risk_level: str = "medium",
        estimated_impact: str = "moderate",
    ) -> CodeChangeProposal:
        """
        Create a code change proposal.

        Args:
            file_path: Path to file to modify
            change_description: Description of the proposed change
            rationale: Why this change should be made
            risk_level: Risk assessment (low, medium, high)
            estimated_impact: Impact assessment

        Returns:
            CodeChangeProposal object

        Example:
            >>> proposal = proposer.propose_change(
            ...     file_path="griptape/engines/query_engine.py",
            ...     change_description="Add caching layer",
            ...     rationale="Improve performance by 40%",
            ...     risk_level="low"
            ... )
        """
        analysis = self.analyze_codebase(file_path)

        impact_analysis = {
            "file_analysis": analysis,
            "risk_level": risk_level,
            "estimated_impact": estimated_impact,
            "proposing_bot": self.bot_id,
            "affected_files": [str(file_path)],
            "requires_testing": self._determine_testing_requirements(risk_level),
        }

        proposal = CodeChangeProposal(
            bot_id=self.bot_id,
            file_path=str(file_path),
            change_description=change_description,
            rationale=rationale,
            impact_analysis=impact_analysis,
            risk_level=risk_level,
            estimated_impact=estimated_impact,
            testing_requirements=self._determine_testing_requirements(risk_level),
        )

        logger.info(f"Created proposal from {self.bot_id}: {change_description} ({risk_level} risk)")
        return proposal

    def _determine_testing_requirements(self, risk_level: str) -> list[str]:
        """
        Determine testing requirements based on risk level.

        Args:
            risk_level: Risk level (low, medium, high)

        Returns:
            List of required tests
        """
        base_requirements = ["unit_tests"]

        if risk_level == "medium":
            base_requirements.extend(["integration_tests"])
        elif risk_level == "high":
            base_requirements.extend(["integration_tests", "system_tests", "manual_review"])

        return base_requirements

    def create_pull_request(
        self, proposal: CodeChangeProposal, code_diff: str | None = None
    ) -> PullRequestResult | None:
        """
        Create a GitHub pull request for the proposal.

        This method creates a new branch, commits changes, creates a PR,
        and requests review from Denauld Brown.

        Args:
            proposal: CodeChangeProposal object
            code_diff: Optional code diff (if None, must be generated separately)

        Returns:
            PullRequestResult if successful, None otherwise

        Example:
            >>> pr_result = proposer.create_pull_request(proposal)
            >>> print(f"Created PR #{pr_result.pr_number}")
        """
        if not self.github_token:
            logger.error("Cannot create PR: No GitHub token available")
            return None

        try:
            # Use PyGithub for GitHub API interaction
            from github import Auth, Github

            auth = Auth.Token(self.github_token)
            g = Github(auth=auth)
            repo = g.get_repo(self.repo_name)

            # Create branch name
            branch_name = f"leadership/{self.bot_id}/{proposal.change_description.lower().replace(' ', '-')[:50]}"

            # Get base branch reference
            base_ref = repo.get_git_ref(f"heads/{self.base_branch}")

            # Create new branch
            try:
                repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=base_ref.object.sha)
                logger.info(f"Created branch: {branch_name}")
            except Exception as e:
                logger.warning(f"Branch may already exist: {e}")

            # Create PR description
            pr_body = self._generate_pr_description(proposal, code_diff)

            # Create pull request
            pr = repo.create_pull(
                title=f"[{self.bot_id}] {proposal.change_description}",
                body=pr_body,
                head=branch_name,
                base=self.base_branch,
            )

            # Add labels
            pr.add_to_labels("leadership-proposed", "awaiting-denauld-approval")

            # Request review from Denauld
            try:
                pr.create_review_request(reviewers=["denauld-brown"])
            except Exception as e:
                logger.warning(f"Could not request review: {e}")

            logger.info(f"Created PR #{pr.number}: {pr.html_url}")

            return PullRequestResult(
                pr_number=pr.number,
                pr_url=pr.html_url,
                branch_name=branch_name,
                proposal_id=f"{self.bot_id}_{proposal.created_at.timestamp()}" if proposal.created_at else f"{self.bot_id}_unknown",
                status="pending_review",
                created_at=datetime.now(UTC),
            )

        except ImportError:
            logger.exception("PyGithub not installed - cannot create PR")
            return None
        except Exception as e:
            logger.exception(f"Error creating pull request: {e}")
            return None

    def _generate_pr_description(self, proposal: CodeChangeProposal, code_diff: str | None) -> str:
        """
        Generate comprehensive PR description.

        Args:
            proposal: CodeChangeProposal object
            code_diff: Optional code diff

        Returns:
            Formatted PR description
        """
        description = f"""## Leadership Code Proposal

**Proposing Bot:** {proposal.bot_id}
**Risk Level:** {proposal.risk_level.upper()}
**Estimated Impact:** {proposal.estimated_impact}

### Change Description
{proposal.change_description}

### Rationale
{proposal.rationale}

### Impact Analysis
- **Affected Files:** {', '.join(proposal.impact_analysis.get('affected_files', []))}
- **Testing Requirements:** {', '.join(proposal.testing_requirements or [])}
- **Risk Assessment:** {proposal.risk_level}

### File Analysis
"""

        if "file_analysis" in proposal.impact_analysis:
            analysis = proposal.impact_analysis["file_analysis"]
            description += f"- **Lines of Code:** {analysis.get('lines_of_code', 'N/A')}\n"
            description += f"- **Complexity Score:** {analysis.get('complexity_score', 'N/A')}/10\n"

            improvements = analysis.get("improvement_opportunities", [])
            if improvements:
                description += f"\n**Improvement Opportunities:**\n"
                for imp in improvements:
                    description += f"- {imp}\n"

        if code_diff:
            description += f"\n### Code Diff\n```diff\n{code_diff}\n```\n"

        description += """
---
**Approval Required:** @denauld-brown (Supreme Authority)

This proposal requires final approval from Denauld Brown before merging.
"""

        return description

    def get_proposal_status(self, pr_number: int) -> dict[str, Any]:
        """
        Get the status of a pull request proposal.

        Args:
            pr_number: GitHub PR number

        Returns:
            Dictionary containing PR status

        Example:
            >>> status = proposer.get_proposal_status(123)
            >>> print(status['state'])
            'open'
        """
        if not self.github_token:
            return {"error": "No GitHub token available"}

        try:
            from github import Auth, Github

            auth = Auth.Token(self.github_token)
            g = Github(auth=auth)
            repo = g.get_repo(self.repo_name)
            pr = repo.get_pull(pr_number)

            return {
                "pr_number": pr.number,
                "state": pr.state,
                "merged": pr.merged,
                "mergeable": pr.mergeable,
                "comments": pr.comments,
                "reviews": [
                    {"user": review.user.login, "state": review.state} for review in pr.get_reviews()
                ],
                "labels": [label.name for label in pr.labels],
            }

        except Exception as e:
            logger.exception(f"Error getting PR status: {e}")
            return {"error": str(e)}

    def __repr__(self) -> str:
        """String representation of CodeProposer."""
        return f"CodeProposer(bot_id='{self.bot_id}', repo='{self.repo_name}')"
