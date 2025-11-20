"""
Decision Router Module

Routes decisions through the leadership hierarchy based on tier levels,
expertise areas, and consensus requirements. Ensures decisions reach the
appropriate authority level and gather necessary approvals.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Sequence

    from griptape.amt.leadership.tier_authority import TierAuthority

logger = logging.getLogger(__name__)


class DecisionComplexity(Enum):
    """Complexity levels for decision routing."""

    TRIVIAL = "trivial"  # Single bot can decide
    MODERATE = "moderate"  # Tier-level consensus needed
    STRATEGIC = "strategic"  # Executive+ approval needed
    CRITICAL = "critical"  # Supreme authority required


class ExpertiseArea(Enum):
    """Areas of expertise for routing to appropriate specialists."""

    LEGAL_COMPLIANCE = "legal_compliance"  # Courtney Sellars
    OPERATIONS = "operations"  # Alexandra Martinez
    STRATEGY = "strategy"  # Marcus Sterling
    PLAYER_DEVELOPMENT = "player_development"  # Darius Washington
    MENTORSHIP = "mentorship"  # Bill McKenzie
    CAREER_DEV = "career_development"  # Patricia Williams
    INNOVATION = "innovation"  # David Kim
    AI_RESEARCH = "ai_research"  # Rachel Foster
    DEVOPS = "devops"  # Jake Morrison
    UX_DESIGN = "ux_design"  # Maya Patel
    AI_COORDINATION = "ai_coordination"  # M.E.L.
    SUPREME_VISION = "supreme_vision"  # Denauld Brown


@dataclass
class RoutingDecision:
    """Result of decision routing."""

    target_bot_ids: list[str]
    requires_consensus: bool
    requires_denauld_approval: bool
    complexity: DecisionComplexity
    reasoning: str


@dataclass
class DecisionContext:
    """Context for a decision that needs to be routed."""

    decision_type: str
    description: str
    complexity: DecisionComplexity
    expertise_required: list[ExpertiseArea]
    requesting_bot_id: str
    metadata: dict[str, Any] | None = None


class DecisionRouter:
    """
    Routes decisions through the leadership hierarchy.

    This class determines which bots should participate in a decision,
    whether consensus is required, and ensures Denauld Brown's approval
    is obtained for critical decisions and code changes.

    Example:
        >>> router = DecisionRouter()
        >>> context = DecisionContext(
        ...     decision_type="code_changes",
        ...     description="Optimize query engine",
        ...     complexity=DecisionComplexity.STRATEGIC,
        ...     expertise_required=[ExpertiseArea.AI_RESEARCH, ExpertiseArea.DEVOPS],
        ...     requesting_bot_id="rachel_foster"
        ... )
        >>> routing = router.route_decision(context, available_authorities)
        >>> print(routing.target_bot_ids)
        ['rachel_foster', 'jake_morrison', 'denauld_brown']
    """

    # Mapping of expertise areas to bot IDs
    EXPERTISE_ROUTING: dict[ExpertiseArea, str] = {
        ExpertiseArea.SUPREME_VISION: "denauld_brown",
        ExpertiseArea.AI_COORDINATION: "mel_digital_twin",
        ExpertiseArea.LEGAL_COMPLIANCE: "courtney_sellars",
        ExpertiseArea.OPERATIONS: "alexandra_martinez",
        ExpertiseArea.STRATEGY: "marcus_sterling",
        ExpertiseArea.PLAYER_DEVELOPMENT: "darius_washington",
        ExpertiseArea.MENTORSHIP: "bill_mckenzie",
        ExpertiseArea.CAREER_DEV: "patricia_williams",
        ExpertiseArea.INNOVATION: "david_kim",
        ExpertiseArea.AI_RESEARCH: "rachel_foster",
        ExpertiseArea.DEVOPS: "jake_morrison",
        ExpertiseArea.UX_DESIGN: "maya_patel",
    }

    def __init__(self) -> None:
        """Initialize DecisionRouter."""
        logger.info("DecisionRouter initialized")

    def route_decision(
        self, context: DecisionContext, available_authorities: Sequence[TierAuthority]
    ) -> RoutingDecision:
        """
        Route a decision to appropriate leadership members.

        Args:
            context: DecisionContext describing the decision
            available_authorities: List of available TierAuthority objects

        Returns:
            RoutingDecision with target bots and requirements

        Example:
            >>> context = DecisionContext(
            ...     decision_type="code_changes",
            ...     description="Add new ML model",
            ...     complexity=DecisionComplexity.STRATEGIC,
            ...     expertise_required=[ExpertiseArea.AI_RESEARCH],
            ...     requesting_bot_id="rachel_foster"
            ... )
            >>> routing = router.route_decision(context, authorities)
        """
        logger.info(f"Routing decision: {context.decision_type} from {context.requesting_bot_id}")

        # Start with expertise-based routing
        target_bot_ids = self._route_by_expertise(context.expertise_required)

        # Add tier-based routing
        tier_targets = self._route_by_tier(context.complexity, available_authorities)
        target_bot_ids.extend(tier_targets)

        # Add requesting bot if not already included
        if context.requesting_bot_id not in target_bot_ids:
            target_bot_ids.append(context.requesting_bot_id)

        # Determine consensus requirement
        requires_consensus = self._requires_consensus(context.complexity, len(target_bot_ids))

        # Determine if Denauld's approval is required
        requires_denauld_approval = self._requires_denauld_approval(context)

        # Ensure Denauld is included if approval required
        if requires_denauld_approval and "denauld_brown" not in target_bot_ids:
            target_bot_ids.append("denauld_brown")

        reasoning = self._generate_routing_reasoning(context, target_bot_ids, requires_consensus)

        routing = RoutingDecision(
            target_bot_ids=list(set(target_bot_ids)),  # Remove duplicates
            requires_consensus=requires_consensus,
            requires_denauld_approval=requires_denauld_approval,
            complexity=context.complexity,
            reasoning=reasoning,
        )

        logger.info(f"Decision routed to {len(routing.target_bot_ids)} bots: {routing.target_bot_ids}")

        return routing

    def _route_by_expertise(self, expertise_areas: Sequence[ExpertiseArea]) -> list[str]:
        """
        Route decision to bots with specific expertise.

        Args:
            expertise_areas: Required areas of expertise

        Returns:
            List of bot IDs with matching expertise
        """
        bot_ids = []
        for area in expertise_areas:
            if area in self.EXPERTISE_ROUTING:
                bot_ids.append(self.EXPERTISE_ROUTING[area])

        logger.debug(f"Expertise routing for {expertise_areas}: {bot_ids}")
        return bot_ids

    def _route_by_tier(
        self, complexity: DecisionComplexity, available_authorities: Sequence[TierAuthority]
    ) -> list[str]:
        """
        Route decision based on complexity and tier levels.

        Args:
            complexity: Decision complexity level
            available_authorities: Available authorities to route to

        Returns:
            List of bot IDs at appropriate tier levels
        """
        from griptape.amt.leadership.tier_authority import AuthorityLevel

        # Map complexity to minimum required tier
        complexity_tier_map = {
            DecisionComplexity.TRIVIAL: AuthorityLevel.INNOVATION,
            DecisionComplexity.MODERATE: AuthorityLevel.STRATEGIC,
            DecisionComplexity.STRATEGIC: AuthorityLevel.EXECUTIVE,
            DecisionComplexity.CRITICAL: AuthorityLevel.SUPREME,
        }

        required_tier = complexity_tier_map[complexity]

        # Get all bots at or above the required tier
        bot_ids = [
            auth.bot_id for auth in available_authorities if auth.tier_level <= required_tier  # Lower tier = higher authority
        ]

        logger.debug(f"Tier routing for {complexity.value}: tier <= {required_tier.value}, bots: {bot_ids}")
        return bot_ids

    def _requires_consensus(self, complexity: DecisionComplexity, participant_count: int) -> bool:
        """
        Determine if consensus is required.

        Args:
            complexity: Decision complexity level
            participant_count: Number of participants

        Returns:
            True if consensus is required
        """
        # Strategic and critical decisions always require consensus
        if complexity in (DecisionComplexity.STRATEGIC, DecisionComplexity.CRITICAL):
            return True

        # Moderate decisions require consensus if multiple participants
        if complexity == DecisionComplexity.MODERATE and participant_count > 1:
            return True

        return False

    def _requires_denauld_approval(self, context: DecisionContext) -> bool:
        """
        Determine if Denauld Brown's approval is required.

        Args:
            context: DecisionContext

        Returns:
            True if Denauld's approval is required
        """
        # Critical decisions always require Denauld
        if context.complexity == DecisionComplexity.CRITICAL:
            return True

        # Code changes always require Denauld
        if context.decision_type == "code_changes":
            return True

        # Strategic decisions require Denauld
        if context.complexity == DecisionComplexity.STRATEGIC:
            return True

        # Hiring and budget decisions require Denauld
        if context.decision_type in ("hiring", "budget"):
            return True

        return False

    def _generate_routing_reasoning(
        self, context: DecisionContext, target_bot_ids: Sequence[str], requires_consensus: bool
    ) -> str:
        """
        Generate human-readable reasoning for routing decision.

        Args:
            context: DecisionContext
            target_bot_ids: Target bot IDs
            requires_consensus: Whether consensus is required

        Returns:
            Reasoning string
        """
        expertise_str = ", ".join([area.value for area in context.expertise_required])

        reasoning = (
            f"Decision '{context.decision_type}' (complexity: {context.complexity.value}) "
            f"routed to {len(target_bot_ids)} bots based on expertise ({expertise_str}) "
            f"and tier requirements. "
        )

        if requires_consensus:
            reasoning += "Consensus required. "

        if "denauld_brown" in target_bot_ids:
            reasoning += "Denauld Brown's final approval required."

        return reasoning

    def handle_consensus(
        self, votes: dict[str, bool], required_threshold: float = 0.67, include_denauld_veto: bool = True
    ) -> tuple[bool, str]:
        """
        Handle consensus building from multiple bots.

        Args:
            votes: Dictionary mapping bot_id to approval (True/False)
            required_threshold: Percentage of approvals required (default 67%)
            include_denauld_veto: If True, Denauld can veto regardless of consensus

        Returns:
            Tuple of (consensus_reached, reasoning)

        Example:
            >>> votes = {
            ...     "rachel_foster": True,
            ...     "jake_morrison": True,
            ...     "david_kim": False,
            ...     "denauld_brown": True
            ... }
            >>> consensus, reason = router.handle_consensus(votes)
            >>> print(consensus)
            True
        """
        if not votes:
            return False, "No votes received"

        # Check for Denauld's veto power
        if include_denauld_veto and "denauld_brown" in votes:
            if not votes["denauld_brown"]:
                return False, "Denauld Brown vetoed the decision (Supreme Authority override)"

        # Calculate approval percentage
        approvals = sum(1 for vote in votes.values() if vote)
        total_votes = len(votes)
        approval_percentage = approvals / total_votes

        consensus_reached = approval_percentage >= required_threshold

        reasoning = (
            f"Consensus {'reached' if consensus_reached else 'not reached'}: "
            f"{approvals}/{total_votes} approvals ({approval_percentage:.1%}), "
            f"threshold: {required_threshold:.1%}"
        )

        logger.info(reasoning)
        return consensus_reached, reasoning

    def escalate_to_tier(self, current_tier: int, escalation_reason: str) -> int:
        """
        Determine which tier to escalate a decision to.

        Args:
            current_tier: Current tier level
            escalation_reason: Reason for escalation

        Returns:
            Target tier level for escalation

        Example:
            >>> router = DecisionRouter()
            >>> target_tier = router.escalate_to_tier(6, "strategic_impact")
            >>> print(target_tier)
            3  # Executive tier
        """
        from griptape.amt.leadership.tier_authority import AuthorityLevel

        # Map escalation reasons to target tiers
        escalation_map = {
            "strategic_impact": AuthorityLevel.EXECUTIVE,
            "legal_concern": AuthorityLevel.EXECUTIVE,
            "high_risk": AuthorityLevel.AI_CORE,
            "emergency": AuthorityLevel.SUPREME,
            "code_security": AuthorityLevel.EXECUTIVE,
        }

        target_tier = escalation_map.get(escalation_reason, AuthorityLevel.STRATEGIC)

        logger.info(f"Escalating from tier {current_tier} to tier {target_tier.value} (reason: {escalation_reason})")

        return target_tier.value

    def __repr__(self) -> str:
        """String representation of DecisionRouter."""
        return "DecisionRouter(expertise_areas=12, complexity_levels=4)"
