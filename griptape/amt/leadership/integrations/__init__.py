"""
External Integrations Module

Provides integration with external systems for the AMT Leadership IKB:
- GitHub API: Pull request creation, code review, repository management
- Figma API: Design system integration (Maya Patel)
- Supabase: Approval dashboard, decision logging, database operations

These integrations enable the leadership bots to interact with external
platforms for code proposals, design collaboration, and approval workflows.

Example:
    >>> from griptape.amt.leadership.integrations import GitHubIntegration, SupabaseDashboard
    >>> github = GitHubIntegration(token="ghp_...")
    >>> pr = github.create_pr(
    ...     repo="AnalyzeMyTeamHQ/analyzemyteam-griptape-core",
    ...     title="Leadership Bot Proposal",
    ...     body="Proposed by rachel_foster",
    ...     head="leadership/rachel_foster/optimization",
    ...     base="main"
    ... )
"""

from __future__ import annotations

from griptape.amt.leadership.integrations.github_integration import GitHubIntegration
from griptape.amt.leadership.integrations.figma_integration import FigmaIntegration
from griptape.amt.leadership.integrations.supabase_dashboard import SupabaseDashboard

__all__ = [
    "GitHubIntegration",
    "FigmaIntegration",
    "SupabaseDashboard",
]
