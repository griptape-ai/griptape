"""
Leadership Coordinator Module

Orchestrates decision routing and collective intelligence across AMT's 12-bot
leadership hierarchy. Manages consensus building, tier escalation, and
integration with external systems.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Sequence

    from griptape.amt.leadership.code_proposer import CodeChangeProposal
    from griptape.amt.leadership.decision_router import DecisionContext, RoutingDecision
    from griptape.amt.leadership.tier_authority import TierAuthority

logger = logging.getLogger(__name__)


@dataclass
class CoordinationResult:
    """Result of a coordination action."""

    success: bool
    decision_id: str
    involved_bots: list[str]
    final_decision: str
    reasoning: str
    timestamp: datetime
    requires_denauld_approval: bool
    metadata: dict[str, Any] | None = None


@dataclass
class LeadershipBot:
    """Represents a leadership bot in the hierarchy."""

    bot_id: str
    full_name: str
    nickname: str
    tier_level: int
    emergency_priority: int
    authority: TierAuthority
    specializations: list[str]
    is_available: bool = True


class LeadershipCoordinator:
    """
    Orchestrates decision-making across the 12-bot leadership hierarchy.

    This is the main coordination class that brings together tier authority,
    decision routing, code proposals, and empire-wide coordination. It manages
    the entire lifecycle of leadership decisions from proposal to approval.

    Attributes:
        leadership_bots: Dictionary mapping bot_id to LeadershipBot
        decision_router: DecisionRouter instance
        decision_log: List of coordination results

    Example:
        >>> coordinator = LeadershipCoordinator()
        >>> coordinator.register_bot(
        ...     bot_id="rachel_foster",
        ...     full_name="Dr. Rachel Foster",
        ...     nickname="The Algorithm",
        ...     tier_level=6,
        ...     emergency_priority=14,
        ...     specializations=["AI Research", "Neural Networks"]
        ... )
        >>> result = coordinator.route_decision(decision_context)
        >>> print(result.final_decision)
    """

    def __init__(self) -> None:
        """Initialize LeadershipCoordinator."""
        from griptape.amt.leadership.decision_router import DecisionRouter

        self.leadership_bots: dict[str, LeadershipBot] = {}
        self.decision_router = DecisionRouter()
        self.decision_log: list[CoordinationResult] = []

        logger.info("LeadershipCoordinator initialized")

    def register_bot(
        self,
        bot_id: str,
        full_name: str,
        nickname: str,
        tier_level: int,
        emergency_priority: int,
        specializations: list[str],
        authority: TierAuthority | None = None,
    ) -> None:
        """
        Register a leadership bot in the hierarchy.

        Args:
            bot_id: Unique bot identifier
            full_name: Full name of the leader
            nickname: Leadership nickname (e.g., "The Mastermind")
            tier_level: Authority tier (1-6)
            emergency_priority: Emergency succession priority
            specializations: List of areas of expertise
            authority: Optional pre-configured TierAuthority

        Example:
            >>> coordinator.register_bot(
            ...     bot_id="denauld_brown",
            ...     full_name="Denauld Brown",
            ...     nickname="The Mastermind",
            ...     tier_level=1,
            ...     emergency_priority=1,
            ...     specializations=["Triangle Defense", "Strategic Vision"]
            ... )
        """
        from griptape.amt.leadership.tier_authority import TierAuthority

        if authority is None:
            authority = TierAuthority(
                bot_id=bot_id, tier_level=tier_level, emergency_priority=emergency_priority
            )

        bot = LeadershipBot(
            bot_id=bot_id,
            full_name=full_name,
            nickname=nickname,
            tier_level=tier_level,
            emergency_priority=emergency_priority,
            authority=authority,
            specializations=specializations,
        )

        self.leadership_bots[bot_id] = bot
        logger.info(f"Registered {full_name} ({nickname}) at tier {tier_level}")

    def get_available_authorities(self) -> list[TierAuthority]:
        """
        Get list of available TierAuthority objects.

        Returns:
            List of TierAuthority for available bots

        Example:
            >>> authorities = coordinator.get_available_authorities()
            >>> print(len(authorities))
            12
        """
        return [bot.authority for bot in self.leadership_bots.values() if bot.is_available]

    def route_decision(self, context: DecisionContext) -> CoordinationResult:
        """
        Route a decision through the leadership hierarchy.

        Args:
            context: DecisionContext describing the decision

        Returns:
            CoordinationResult with final decision and routing

        Example:
            >>> from griptape.amt.leadership.decision_router import DecisionContext, DecisionComplexity, ExpertiseArea
            >>> context = DecisionContext(
            ...     decision_type="code_changes",
            ...     description="Optimize query engine",
            ...     complexity=DecisionComplexity.STRATEGIC,
            ...     expertise_required=[ExpertiseArea.AI_RESEARCH],
            ...     requesting_bot_id="rachel_foster"
            ... )
            >>> result = coordinator.route_decision(context)
        """
        logger.info(f"Routing decision from {context.requesting_bot_id}: {context.decision_type}")

        # Get routing decision
        authorities = self.get_available_authorities()
        routing = self.decision_router.route_decision(context, authorities)

        # Build coordination result
        result = CoordinationResult(
            success=True,
            decision_id=self._generate_decision_id(context),
            involved_bots=routing.target_bot_ids,
            final_decision="pending_approval" if routing.requires_denauld_approval else "approved",
            reasoning=routing.reasoning,
            timestamp=datetime.now(UTC),
            requires_denauld_approval=routing.requires_denauld_approval,
            metadata={"routing": routing, "context": context},
        )

        # Log the decision
        self.decision_log.append(result)

        logger.info(
            f"Decision {result.decision_id} routed to {len(result.involved_bots)} bots, "
            f"Denauld approval: {result.requires_denauld_approval}"
        )

        return result

    def coordinate_empire(self, operation: str, companies: Sequence[str], metadata: dict[str, Any] | None = None) -> CoordinationResult:
        """
        Coordinate empire-wide operations across multiple companies.

        Args:
            operation: Type of operation (e.g., "resource_allocation", "strategic_alignment")
            companies: List of company names to coordinate
            metadata: Optional metadata about the operation

        Returns:
            CoordinationResult

        Example:
            >>> result = coordinator.coordinate_empire(
            ...     operation="strategic_alignment",
            ...     companies=["Company1", "Company2", "Company3"],
            ...     metadata={"quarter": "Q1", "focus": "growth"}
            ... )
        """
        from griptape.amt.leadership.decision_router import DecisionComplexity, DecisionContext, ExpertiseArea

        logger.info(f"Coordinating empire operation '{operation}' across {len(companies)} companies")

        # Create decision context for empire coordination
        context = DecisionContext(
            decision_type="empire_coordination",
            description=f"{operation} across {len(companies)} companies",
            complexity=DecisionComplexity.STRATEGIC,
            expertise_required=[ExpertiseArea.OPERATIONS, ExpertiseArea.STRATEGY],
            requesting_bot_id="mel_digital_twin",  # M.E.L. typically coordinates empire ops
            metadata=metadata or {},
        )

        # Route through decision system
        result = self.route_decision(context)

        # Update result with empire-specific info
        result.metadata = result.metadata or {}
        result.metadata["empire_operation"] = {
            "operation": operation,
            "companies": list(companies),
            "coordination_timestamp": datetime.now(UTC),
        }

        logger.info(f"Empire coordination result: {result.final_decision}")
        return result

    def escalate_to_tier(self, current_decision_id: str, escalation_reason: str) -> CoordinationResult | None:
        """
        Escalate a decision to a higher tier.

        Args:
            current_decision_id: ID of decision to escalate
            escalation_reason: Reason for escalation

        Returns:
            New CoordinationResult for escalated decision, or None if not found

        Example:
            >>> result = coordinator.escalate_to_tier(
            ...     current_decision_id="decision_123",
            ...     escalation_reason="strategic_impact"
            ... )
        """
        # Find original decision
        original_decision = None
        for decision in self.decision_log:
            if decision.decision_id == current_decision_id:
                original_decision = decision
                break

        if not original_decision:
            logger.error(f"Decision {current_decision_id} not found for escalation")
            return None

        logger.info(f"Escalating decision {current_decision_id}, reason: {escalation_reason}")

        # Get original context
        original_context = original_decision.metadata.get("context") if original_decision.metadata else None

        if not original_context:
            logger.error(f"No context found for decision {current_decision_id}")
            return None

        # Determine new tier
        current_tier = min([self.leadership_bots[bot_id].tier_level for bot_id in original_decision.involved_bots])
        new_tier = self.decision_router.escalate_to_tier(current_tier, escalation_reason)

        # Create escalated decision context
        from griptape.amt.leadership.decision_router import DecisionComplexity

        escalated_context = DecisionContext(
            decision_type=original_context.decision_type,
            description=f"ESCALATED: {original_context.description}",
            complexity=DecisionComplexity.CRITICAL if new_tier <= 2 else DecisionComplexity.STRATEGIC,
            expertise_required=original_context.expertise_required,
            requesting_bot_id=original_context.requesting_bot_id,
            metadata={"escalation_reason": escalation_reason, "original_decision_id": current_decision_id},
        )

        # Route escalated decision
        escalated_result = self.route_decision(escalated_context)

        logger.info(f"Decision escalated from tier {current_tier} to tier {new_tier}")
        return escalated_result

    def handle_code_proposal(self, proposal: CodeChangeProposal) -> CoordinationResult:
        """
        Handle a code change proposal from a leadership bot.

        Args:
            proposal: CodeChangeProposal object

        Returns:
            CoordinationResult

        Example:
            >>> from griptape.amt.leadership.code_proposer import CodeProposer
            >>> proposer = CodeProposer(bot_id="rachel_foster")
            >>> proposal = proposer.propose_change(
            ...     file_path="griptape/engines/query_engine.py",
            ...     change_description="Add caching",
            ...     rationale="Improve performance"
            ... )
            >>> result = coordinator.handle_code_proposal(proposal)
        """
        from griptape.amt.leadership.decision_router import DecisionComplexity, DecisionContext, ExpertiseArea

        logger.info(f"Handling code proposal from {proposal.bot_id}: {proposal.change_description}")

        # Map risk level to complexity
        risk_complexity_map = {
            "low": DecisionComplexity.MODERATE,
            "medium": DecisionComplexity.STRATEGIC,
            "high": DecisionComplexity.CRITICAL,
        }

        complexity = risk_complexity_map.get(proposal.risk_level, DecisionComplexity.STRATEGIC)

        # Determine required expertise based on file path
        expertise_required = [ExpertiseArea.AI_COORDINATION]

        if "test" in proposal.file_path.lower():
            expertise_required.append(ExpertiseArea.DEVOPS)
        if "ui" in proposal.file_path.lower() or "frontend" in proposal.file_path.lower():
            expertise_required.append(ExpertiseArea.UX_DESIGN)

        # Create decision context
        context = DecisionContext(
            decision_type="code_changes",
            description=proposal.change_description,
            complexity=complexity,
            expertise_required=expertise_required,
            requesting_bot_id=proposal.bot_id,
            metadata={"proposal": proposal, "impact_analysis": proposal.impact_analysis},
        )

        # Route the decision
        result = self.route_decision(context)

        logger.info(f"Code proposal requires approval from: {', '.join(result.involved_bots)}")
        return result

    def build_consensus(
        self, decision_id: str, votes: dict[str, bool], threshold: float = 0.67
    ) -> tuple[bool, str]:
        """
        Build consensus on a decision from multiple bots.

        Args:
            decision_id: ID of the decision
            votes: Dictionary mapping bot_id to approval (True/False)
            threshold: Approval threshold (default 67%)

        Returns:
            Tuple of (consensus_reached, reasoning)

        Example:
            >>> votes = {
            ...     "rachel_foster": True,
            ...     "jake_morrison": True,
            ...     "denauld_brown": True
            ... }
            >>> consensus, reason = coordinator.build_consensus("decision_123", votes)
        """
        logger.info(f"Building consensus for decision {decision_id} with {len(votes)} votes")

        consensus, reasoning = self.decision_router.handle_consensus(votes, threshold)

        # Update decision log
        for decision in self.decision_log:
            if decision.decision_id == decision_id:
                decision.final_decision = "approved" if consensus else "rejected"
                decision.metadata = decision.metadata or {}
                decision.metadata["consensus"] = {"votes": votes, "reasoning": reasoning}
                break

        logger.info(f"Consensus for {decision_id}: {consensus}")
        return consensus, reasoning

    def _generate_decision_id(self, context: DecisionContext) -> str:
        """
        Generate unique decision ID.

        Args:
            context: DecisionContext

        Returns:
            Unique decision ID
        """
        timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
        return f"{context.requesting_bot_id}_{context.decision_type}_{timestamp}"

    def get_bot_status(self, bot_id: str) -> dict[str, Any]:
        """
        Get status and information about a leadership bot.

        Args:
            bot_id: Bot identifier

        Returns:
            Dictionary with bot status and info

        Example:
            >>> status = coordinator.get_bot_status("denauld_brown")
            >>> print(status['nickname'])
            'The Mastermind'
        """
        if bot_id not in self.leadership_bots:
            return {"error": "Bot not found", "bot_id": bot_id}

        bot = self.leadership_bots[bot_id]

        return {
            "bot_id": bot.bot_id,
            "full_name": bot.full_name,
            "nickname": bot.nickname,
            "tier_level": bot.tier_level,
            "emergency_priority": bot.emergency_priority,
            "specializations": bot.specializations,
            "is_available": bot.is_available,
            "can_propose_code": bot.authority.validate_authority("code_changes"),
            "requires_approval": bot.authority.permissions.final_approval_required,
        }

    def get_decision_history(self, limit: int = 10) -> list[dict[str, Any]]:
        """
        Get recent decision history.

        Args:
            limit: Maximum number of decisions to return

        Returns:
            List of decision summaries

        Example:
            >>> history = coordinator.get_decision_history(limit=5)
            >>> print(len(history))
            5
        """
        recent_decisions = sorted(self.decision_log, key=lambda d: d.timestamp, reverse=True)[:limit]

        return [
            {
                "decision_id": d.decision_id,
                "involved_bots": d.involved_bots,
                "final_decision": d.final_decision,
                "timestamp": d.timestamp.isoformat(),
                "requires_denauld_approval": d.requires_denauld_approval,
            }
            for d in recent_decisions
        ]

    def __repr__(self) -> str:
        """String representation of LeadershipCoordinator."""
        return f"LeadershipCoordinator(bots={len(self.leadership_bots)}, decisions={len(self.decision_log)})"
