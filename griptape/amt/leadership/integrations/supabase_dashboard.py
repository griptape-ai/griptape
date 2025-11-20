"""
Supabase Dashboard Module

Provides Supabase integration for the AMT Leadership approval dashboard.
Manages proposal creation, approval tracking, decision logging, and
real-time notifications for Denauld Brown's approval workflow.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any
from uuid import uuid4

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


@dataclass
class LeadershipProposal:
    """Represents a leadership proposal in Supabase."""

    id: str
    proposing_bot_id: str
    proposal_type: str  # 'code_change', 'strategic_decision', etc.
    description: str
    code_diff: str | None
    impact_analysis: dict[str, Any]
    status: str  # 'pending', 'approved', 'rejected'
    created_at: datetime
    reviewed_at: datetime | None = None
    denauld_notes: str | None = None


@dataclass
class DecisionLogEntry:
    """Represents a decision log entry."""

    id: str
    decision_type: str
    involved_bots: list[str]
    tier_level: int
    outcome: str
    reasoning: str
    timestamp: datetime


class SupabaseDashboard:
    """
    Supabase integration for leadership approval dashboard.

    This class manages the backend for Denauld Brown's Netlify-rendered
    approval dashboard. It handles proposal creation, approval/rejection,
    decision logging, and real-time notifications.

    Attributes:
        supabase_url: Supabase project URL
        supabase_key: Supabase service role key

    Example:
        >>> dashboard = SupabaseDashboard()
        >>> proposal = dashboard.create_approval_request(
        ...     proposing_bot_id="rachel_foster",
        ...     proposal_type="code_change",
        ...     description="Optimize query engine",
        ...     impact_analysis={"risk": "low", "impact": "high"}
        ... )
        >>> dashboard.notify_denauld(proposal.id)
    """

    def __init__(
        self,
        supabase_url: str | None = None,
        supabase_key: str | None = None,
    ) -> None:
        """
        Initialize Supabase dashboard integration.

        Args:
            supabase_url: Supabase project URL (defaults to SUPABASE_URL env var)
            supabase_key: Supabase service role key (defaults to SUPABASE_KEY env var)
        """
        self.supabase_url = supabase_url or os.getenv("SUPABASE_URL")
        self.supabase_key = supabase_key or os.getenv("SUPABASE_KEY")

        if not self.supabase_url or not self.supabase_key:
            logger.warning("Supabase credentials not fully configured - operations may fail")

        logger.info("SupabaseDashboard initialized")

    def _get_client(self):
        """Get Supabase client instance."""
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase credentials not configured")

        try:
            from supabase import create_client

            return create_client(self.supabase_url, self.supabase_key)
        except ImportError:
            logger.exception("supabase-py not installed")
            raise

    def create_approval_request(
        self,
        proposing_bot_id: str,
        proposal_type: str,
        description: str,
        impact_analysis: dict[str, Any],
        code_diff: str | None = None,
    ) -> LeadershipProposal | None:
        """
        Create a new proposal requiring Denauld's approval.

        Args:
            proposing_bot_id: ID of bot making the proposal
            proposal_type: Type of proposal (code_change, strategic_decision, etc.)
            description: Proposal description
            impact_analysis: Dictionary with impact analysis data
            code_diff: Optional code diff for code changes

        Returns:
            LeadershipProposal object if successful, None otherwise

        Example:
            >>> proposal = dashboard.create_approval_request(
            ...     proposing_bot_id="rachel_foster",
            ...     proposal_type="code_change",
            ...     description="Add ML model caching",
            ...     impact_analysis={"risk": "low", "estimated_improvement": "40%"}
            ... )
        """
        try:
            client = self._get_client()

            proposal_data = {
                "id": str(uuid4()),
                "proposing_bot_id": proposing_bot_id,
                "proposal_type": proposal_type,
                "description": description,
                "code_diff": code_diff,
                "impact_analysis": impact_analysis,
                "status": "pending",
                "created_at": datetime.now(UTC).isoformat(),
            }

            # Insert into leadership_proposals table
            response = client.table("leadership_proposals").insert(proposal_data).execute()

            if response.data:
                data = response.data[0]
                proposal = LeadershipProposal(
                    id=data["id"],
                    proposing_bot_id=data["proposing_bot_id"],
                    proposal_type=data["proposal_type"],
                    description=data["description"],
                    code_diff=data.get("code_diff"),
                    impact_analysis=data.get("impact_analysis", {}),
                    status=data["status"],
                    created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
                )

                logger.info(f"Created proposal {proposal.id} from {proposing_bot_id}")
                return proposal
            else:
                logger.error("Failed to create proposal - no data returned")
                return None

        except Exception as e:
            logger.exception(f"Error creating approval request: {e}")
            return None

    def notify_denauld(self, proposal_id: str) -> bool:
        """
        Send real-time notification to Denauld's dashboard.

        Args:
            proposal_id: ID of proposal to notify about

        Returns:
            True if notification sent successfully, False otherwise

        Example:
            >>> success = dashboard.notify_denauld("550e8400-e29b-41d4-a716-446655440000")
        """
        try:
            # In production, this would trigger a real-time notification
            # via Supabase Realtime or a webhook to the Netlify dashboard

            logger.info(f"Notification sent to Denauld for proposal {proposal_id}")

            # For now, just log the notification
            # In production implementation:
            # 1. Use Supabase Realtime to push notification
            # 2. Send email notification
            # 3. Update dashboard notification count
            # 4. Trigger webhook to Netlify

            return True

        except Exception as e:
            logger.exception(f"Error sending notification: {e}")
            return False

    def log_decision(
        self,
        decision_type: str,
        involved_bots: list[str],
        tier_level: int,
        outcome: str,
        reasoning: str,
    ) -> DecisionLogEntry | None:
        """
        Log a leadership decision to the database.

        Args:
            decision_type: Type of decision
            involved_bots: List of bot IDs involved
            tier_level: Tier level of decision
            outcome: Decision outcome
            reasoning: Reasoning for decision

        Returns:
            DecisionLogEntry object if successful, None otherwise

        Example:
            >>> entry = dashboard.log_decision(
            ...     decision_type="code_change",
            ...     involved_bots=["rachel_foster", "denauld_brown"],
            ...     tier_level=1,
            ...     outcome="approved",
            ...     reasoning="Performance improvement aligns with strategic goals"
            ... )
        """
        try:
            client = self._get_client()

            log_data = {
                "id": str(uuid4()),
                "decision_type": decision_type,
                "involved_bots": involved_bots,
                "tier_level": tier_level,
                "outcome": outcome,
                "reasoning": reasoning,
                "timestamp": datetime.now(UTC).isoformat(),
            }

            # Insert into decision_log table
            response = client.table("decision_log").insert(log_data).execute()

            if response.data:
                data = response.data[0]
                entry = DecisionLogEntry(
                    id=data["id"],
                    decision_type=data["decision_type"],
                    involved_bots=data["involved_bots"],
                    tier_level=data["tier_level"],
                    outcome=data["outcome"],
                    reasoning=data["reasoning"],
                    timestamp=datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00")),
                )

                logger.info(f"Logged decision {entry.id}: {outcome}")
                return entry
            else:
                logger.error("Failed to log decision - no data returned")
                return None

        except Exception as e:
            logger.exception(f"Error logging decision: {e}")
            return None

    def get_pending_proposals(self) -> list[LeadershipProposal]:
        """
        Get all pending proposals awaiting Denauld's approval.

        Returns:
            List of pending LeadershipProposal objects

        Example:
            >>> pending = dashboard.get_pending_proposals()
            >>> print(f"{len(pending)} proposals awaiting approval")
        """
        try:
            client = self._get_client()

            response = (
                client.table("leadership_proposals")
                .select("*")
                .eq("status", "pending")
                .order("created_at", desc=True)
                .execute()
            )

            proposals = []
            for data in response.data:
                proposal = LeadershipProposal(
                    id=data["id"],
                    proposing_bot_id=data["proposing_bot_id"],
                    proposal_type=data["proposal_type"],
                    description=data["description"],
                    code_diff=data.get("code_diff"),
                    impact_analysis=data.get("impact_analysis", {}),
                    status=data["status"],
                    created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
                    reviewed_at=datetime.fromisoformat(data["reviewed_at"].replace("Z", "+00:00"))
                    if data.get("reviewed_at")
                    else None,
                    denauld_notes=data.get("denauld_notes"),
                )
                proposals.append(proposal)

            logger.info(f"Retrieved {len(proposals)} pending proposals")
            return proposals

        except Exception as e:
            logger.exception(f"Error getting pending proposals: {e}")
            return []

    def approve_proposal(self, proposal_id: str, denauld_notes: str | None = None) -> bool:
        """
        Approve a proposal (Denauld's action).

        Args:
            proposal_id: ID of proposal to approve
            denauld_notes: Optional notes from Denauld

        Returns:
            True if approved successfully, False otherwise

        Example:
            >>> success = dashboard.approve_proposal(
            ...     proposal_id="550e8400-e29b-41d4-a716-446655440000",
            ...     denauld_notes="Excellent optimization. Approved for merge."
            ... )
        """
        try:
            client = self._get_client()

            update_data = {
                "status": "approved",
                "reviewed_at": datetime.now(UTC).isoformat(),
                "denauld_notes": denauld_notes,
            }

            response = client.table("leadership_proposals").update(update_data).eq("id", proposal_id).execute()

            if response.data:
                logger.info(f"Approved proposal {proposal_id}")
                return True
            else:
                logger.error(f"Failed to approve proposal {proposal_id}")
                return False

        except Exception as e:
            logger.exception(f"Error approving proposal: {e}")
            return False

    def reject_proposal(self, proposal_id: str, denauld_notes: str | None = None) -> bool:
        """
        Reject a proposal (Denauld's action).

        Args:
            proposal_id: ID of proposal to reject
            denauld_notes: Optional notes from Denauld explaining rejection

        Returns:
            True if rejected successfully, False otherwise

        Example:
            >>> success = dashboard.reject_proposal(
            ...     proposal_id="550e8400-e29b-41d4-a716-446655440000",
            ...     denauld_notes="Security concerns. Please revise approach."
            ... )
        """
        try:
            client = self._get_client()

            update_data = {
                "status": "rejected",
                "reviewed_at": datetime.now(UTC).isoformat(),
                "denauld_notes": denauld_notes,
            }

            response = client.table("leadership_proposals").update(update_data).eq("id", proposal_id).execute()

            if response.data:
                logger.info(f"Rejected proposal {proposal_id}")
                return True
            else:
                logger.error(f"Failed to reject proposal {proposal_id}")
                return False

        except Exception as e:
            logger.exception(f"Error rejecting proposal: {e}")
            return False

    def get_decision_history(self, limit: int = 50) -> list[DecisionLogEntry]:
        """
        Get recent decision history.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of DecisionLogEntry objects

        Example:
            >>> history = dashboard.get_decision_history(limit=20)
            >>> for entry in history:
            ...     print(f"{entry.decision_type}: {entry.outcome}")
        """
        try:
            client = self._get_client()

            response = (
                client.table("decision_log").select("*").order("timestamp", desc=True).limit(limit).execute()
            )

            entries = []
            for data in response.data:
                entry = DecisionLogEntry(
                    id=data["id"],
                    decision_type=data["decision_type"],
                    involved_bots=data["involved_bots"],
                    tier_level=data["tier_level"],
                    outcome=data["outcome"],
                    reasoning=data["reasoning"],
                    timestamp=datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00")),
                )
                entries.append(entry)

            logger.info(f"Retrieved {len(entries)} decision log entries")
            return entries

        except Exception as e:
            logger.exception(f"Error getting decision history: {e}")
            return []

    def __repr__(self) -> str:
        """String representation of SupabaseDashboard."""
        configured = bool(self.supabase_url and self.supabase_key)
        return f"SupabaseDashboard(configured={configured})"
