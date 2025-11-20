"""
AMT Leadership IKB Module

This module provides the Intelligent Knowledge Base (IKB) system for
AnalyzeMyTeam's 12-bot leadership hierarchy. It enables AI-driven decision-making,
code change proposals, and empire-wide coordination across 12 companies.

Key Components:
    - LeadershipCoordinator: Orchestrates decision routing and collective intelligence
    - CodeProposer: Manages GitHub-integrated code change proposals
    - TierAuthority: Enforces 4-tier authority levels
    - DecisionRouter: Routes decisions by tier and expertise
    - EmpireOrchestrator: Coordinates cross-company operations

Leadership Tiers:
    Tier 1: Supreme Authority (Denauld Brown)
    Tier 2: AI Core (M.E.L.)
    Tier 3: Executive Command (Courtney Sellars, Alexandra Martinez)
    Tier 4: Strategic Leadership (Marcus Sterling, Darius Washington)
    Tier 5: Advisory (Bill McKenzie, Patricia Williams)
    Tier 6: Innovation Team (David Kim, Rachel Foster, Jake Morrison, Maya Patel)

External Integrations:
    - GitHub API: Pull request creation and code review
    - Supabase: Approval dashboard and decision logging
    - Figma API: Design system integration (Maya Patel)
    - Netlify: Dashboard rendering

Example:
    >>> from griptape.amt.leadership import LeadershipCoordinator, CodeProposer
    >>> coordinator = LeadershipCoordinator()
    >>> proposer = CodeProposer(bot_id="rachel_foster")
    >>> proposal = proposer.propose_change(
    ...     file_path="griptape/engines/query_engine.py",
    ...     change_description="Optimize query performance",
    ...     rationale="Reduce latency by 40%"
    ... )
    >>> decision = coordinator.route_decision(proposal)
"""

from __future__ import annotations

from griptape.amt.leadership.coordinator import LeadershipCoordinator
from griptape.amt.leadership.code_proposer import CodeProposer
from griptape.amt.leadership.tier_authority import TierAuthority
from griptape.amt.leadership.decision_router import DecisionRouter
from griptape.amt.leadership.empire_orchestrator import EmpireOrchestrator

__all__ = [
    "LeadershipCoordinator",
    "CodeProposer",
    "TierAuthority",
    "DecisionRouter",
    "EmpireOrchestrator",
]
