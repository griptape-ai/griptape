"""
GitHub Integration Module

Provides GitHub API integration for the AMT Leadership IKB system.
Handles repository operations, pull request creation, code review requests,
and GitHub Actions workflow management.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Sequence

logger = logging.getLogger(__name__)


@dataclass
class GitHubPullRequest:
    """Represents a GitHub pull request."""

    number: int
    title: str
    url: str
    state: str
    merged: bool
    created_at: datetime
    updated_at: datetime
    author: str


@dataclass
class GitHubRepository:
    """Represents a GitHub repository."""

    name: str
    full_name: str
    owner: str
    default_branch: str
    private: bool


class GitHubIntegration:
    """
    GitHub API integration for leadership bot code proposals.

    This class provides methods to interact with GitHub for creating pull requests,
    requesting reviews, managing branches, and tracking proposal status.

    Attributes:
        token: GitHub Personal Access Token
        default_repo: Default repository full name

    Example:
        >>> github = GitHubIntegration(
        ...     token="ghp_xxx",
        ...     default_repo="AnalyzeMyTeamHQ/analyzemyteam-griptape-core"
        ... )
        >>> pr = github.create_pr(
        ...     title="Optimize query engine",
        ...     body="Proposed by rachel_foster",
        ...     head="leadership/rachel_foster/optimization",
        ...     base="main"
        ... )
    """

    def __init__(
        self,
        token: str | None = None,
        default_repo: str = "AnalyzeMyTeamHQ/analyzemyteam-griptape-core",
    ) -> None:
        """
        Initialize GitHub integration.

        Args:
            token: GitHub Personal Access Token (defaults to GITHUB_PAT env var)
            default_repo: Default repository full name
        """
        self.token = token or os.getenv("GITHUB_PAT")
        self.default_repo = default_repo

        if not self.token:
            logger.warning("No GitHub token provided - operations will fail")

        logger.info(f"GitHubIntegration initialized for {default_repo}")

    def authenticate(self) -> bool:
        """
        Test GitHub authentication.

        Returns:
            True if authentication successful, False otherwise

        Example:
            >>> github = GitHubIntegration()
            >>> if github.authenticate():
            ...     print("Connected to GitHub")
        """
        if not self.token:
            logger.error("No token available for authentication")
            return False

        try:
            from github import Auth, Github

            auth = Auth.Token(self.token)
            g = Github(auth=auth)

            # Test authentication by getting user info
            user = g.get_user()
            logger.info(f"Authenticated as GitHub user: {user.login}")
            return True

        except ImportError:
            logger.exception("PyGithub not installed")
            return False
        except Exception as e:
            logger.exception(f"Authentication failed: {e}")
            return False

    def create_pr(
        self,
        title: str,
        body: str,
        head: str,
        base: str = "main",
        repo: str | None = None,
        labels: Sequence[str] | None = None,
        reviewers: Sequence[str] | None = None,
    ) -> GitHubPullRequest | None:
        """
        Create a pull request.

        Args:
            title: PR title
            body: PR description
            head: Head branch (source of changes)
            base: Base branch (target for merge)
            repo: Repository full name (defaults to default_repo)
            labels: Labels to add to PR
            reviewers: GitHub usernames to request review from

        Returns:
            GitHubPullRequest object if successful, None otherwise

        Example:
            >>> pr = github.create_pr(
            ...     title="[rachel_foster] Optimize caching",
            ...     body="Performance improvement proposal",
            ...     head="leadership/rachel_foster/caching",
            ...     labels=["leadership-proposed", "awaiting-denauld-approval"],
            ...     reviewers=["denauld-brown"]
            ... )
        """
        if not self.token:
            logger.error("Cannot create PR: No token available")
            return None

        repo_name = repo or self.default_repo

        try:
            from github import Auth, Github

            auth = Auth.Token(self.token)
            g = Github(auth=auth)
            repository = g.get_repo(repo_name)

            # Create pull request
            pr = repository.create_pull(title=title, body=body, head=head, base=base)

            # Add labels if provided
            if labels:
                try:
                    pr.add_to_labels(*labels)
                except Exception as e:
                    logger.warning(f"Failed to add labels: {e}")

            # Request reviews if provided
            if reviewers:
                try:
                    pr.create_review_request(reviewers=list(reviewers))
                except Exception as e:
                    logger.warning(f"Failed to request reviews: {e}")

            logger.info(f"Created PR #{pr.number}: {pr.html_url}")

            return GitHubPullRequest(
                number=pr.number,
                title=pr.title,
                url=pr.html_url,
                state=pr.state,
                merged=pr.merged,
                created_at=pr.created_at.replace(tzinfo=UTC) if pr.created_at else datetime.now(UTC),
                updated_at=pr.updated_at.replace(tzinfo=UTC) if pr.updated_at else datetime.now(UTC),
                author=pr.user.login if pr.user else "unknown",
            )

        except ImportError:
            logger.exception("PyGithub not installed")
            return None
        except Exception as e:
            logger.exception(f"Error creating PR: {e}")
            return None

    def get_diff(self, pr_number: int, repo: str | None = None) -> str | None:
        """
        Get the diff for a pull request.

        Args:
            pr_number: PR number
            repo: Repository full name (defaults to default_repo)

        Returns:
            Diff string if successful, None otherwise

        Example:
            >>> diff = github.get_diff(pr_number=123)
            >>> print(diff[:100])
        """
        if not self.token:
            logger.error("Cannot get diff: No token available")
            return None

        repo_name = repo or self.default_repo

        try:
            from github import Auth, Github

            auth = Auth.Token(self.token)
            g = Github(auth=auth)
            repository = g.get_repo(repo_name)
            pr = repository.get_pull(pr_number)

            # Get files changed
            files = pr.get_files()
            diff_parts = []

            for file in files:
                diff_parts.append(f"\n{'=' * 60}")
                diff_parts.append(f"File: {file.filename}")
                diff_parts.append(f"Status: {file.status}")
                diff_parts.append(f"Changes: +{file.additions} -{file.deletions}")
                diff_parts.append(f"{'=' * 60}")
                if file.patch:
                    diff_parts.append(file.patch)

            return "\n".join(diff_parts)

        except Exception as e:
            logger.exception(f"Error getting diff: {e}")
            return None

    def request_review(
        self, pr_number: int, reviewers: Sequence[str], repo: str | None = None
    ) -> bool:
        """
        Request review from specific users.

        Args:
            pr_number: PR number
            reviewers: GitHub usernames to request review from
            repo: Repository full name (defaults to default_repo)

        Returns:
            True if successful, False otherwise

        Example:
            >>> success = github.request_review(
            ...     pr_number=123,
            ...     reviewers=["denauld-brown"]
            ... )
        """
        if not self.token:
            logger.error("Cannot request review: No token available")
            return False

        repo_name = repo or self.default_repo

        try:
            from github import Auth, Github

            auth = Auth.Token(self.token)
            g = Github(auth=auth)
            repository = g.get_repo(repo_name)
            pr = repository.get_pull(pr_number)

            pr.create_review_request(reviewers=list(reviewers))
            logger.info(f"Requested review from {reviewers} on PR #{pr_number}")
            return True

        except Exception as e:
            logger.exception(f"Error requesting review: {e}")
            return False

    def get_pr_status(self, pr_number: int, repo: str | None = None) -> dict[str, Any]:
        """
        Get detailed status of a pull request.

        Args:
            pr_number: PR number
            repo: Repository full name (defaults to default_repo)

        Returns:
            Dictionary with PR status information

        Example:
            >>> status = github.get_pr_status(123)
            >>> print(status['state'])
            'open'
        """
        if not self.token:
            return {"error": "No token available"}

        repo_name = repo or self.default_repo

        try:
            from github import Auth, Github

            auth = Auth.Token(self.token)
            g = Github(auth=auth)
            repository = g.get_repo(repo_name)
            pr = repository.get_pull(pr_number)

            reviews = []
            for review in pr.get_reviews():
                reviews.append(
                    {
                        "user": review.user.login if review.user else "unknown",
                        "state": review.state,
                        "submitted_at": review.submitted_at.isoformat() if review.submitted_at else None,
                    }
                )

            return {
                "number": pr.number,
                "title": pr.title,
                "state": pr.state,
                "merged": pr.merged,
                "mergeable": pr.mergeable,
                "mergeable_state": pr.mergeable_state,
                "comments": pr.comments,
                "reviews": reviews,
                "labels": [label.name for label in pr.labels],
                "url": pr.html_url,
                "created_at": pr.created_at.isoformat() if pr.created_at else None,
                "updated_at": pr.updated_at.isoformat() if pr.updated_at else None,
            }

        except Exception as e:
            logger.exception(f"Error getting PR status: {e}")
            return {"error": str(e)}

    def create_branch(
        self, branch_name: str, base_branch: str = "main", repo: str | None = None
    ) -> bool:
        """
        Create a new branch from base branch.

        Args:
            branch_name: Name of new branch
            base_branch: Branch to create from
            repo: Repository full name (defaults to default_repo)

        Returns:
            True if successful, False otherwise

        Example:
            >>> success = github.create_branch(
            ...     branch_name="leadership/rachel_foster/optimization",
            ...     base_branch="main"
            ... )
        """
        if not self.token:
            logger.error("Cannot create branch: No token available")
            return False

        repo_name = repo or self.default_repo

        try:
            from github import Auth, Github

            auth = Auth.Token(self.token)
            g = Github(auth=auth)
            repository = g.get_repo(repo_name)

            # Get base branch reference
            base_ref = repository.get_git_ref(f"heads/{base_branch}")

            # Create new branch
            repository.create_git_ref(ref=f"refs/heads/{branch_name}", sha=base_ref.object.sha)

            logger.info(f"Created branch '{branch_name}' from '{base_branch}'")
            return True

        except Exception as e:
            logger.exception(f"Error creating branch: {e}")
            return False

    def get_repository_info(self, repo: str | None = None) -> GitHubRepository | None:
        """
        Get repository information.

        Args:
            repo: Repository full name (defaults to default_repo)

        Returns:
            GitHubRepository object if successful, None otherwise

        Example:
            >>> repo_info = github.get_repository_info()
            >>> print(repo_info.default_branch)
            'main'
        """
        if not self.token:
            logger.error("Cannot get repository: No token available")
            return None

        repo_name = repo or self.default_repo

        try:
            from github import Auth, Github

            auth = Auth.Token(self.token)
            g = Github(auth=auth)
            repository = g.get_repo(repo_name)

            return GitHubRepository(
                name=repository.name,
                full_name=repository.full_name,
                owner=repository.owner.login if repository.owner else "unknown",
                default_branch=repository.default_branch,
                private=repository.private,
            )

        except Exception as e:
            logger.exception(f"Error getting repository: {e}")
            return None

    def __repr__(self) -> str:
        """String representation of GitHubIntegration."""
        has_token = bool(self.token)
        return f"GitHubIntegration(repo='{self.default_repo}', authenticated={has_token})"
