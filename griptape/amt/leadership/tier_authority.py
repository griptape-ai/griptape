"""
Tier Authority Module

Enforces the 4-tier leadership authority system for AMT's 12-bot hierarchy.
Validates permissions, checks emergency priorities, and enforces approval chains.

Authority Levels:
    - Supreme: Tier 1 (Denauld Brown) - Cannot be overridden
    - AI Core: Tier 2 (M.E.L.) - Emergency continuity
    - Executive: Tier 3 (Courtney Sellars, Alexandra Martinez)
    - Strategic: Tier 4 (Marcus Sterling, Darius Washington)
    - Advisory: Tier 5 (Bill McKenzie, Patricia Williams)
    - Innovation: Tier 6 (David Kim, Rachel Foster, Jake Morrison, Maya Patel)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import IntEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

logger = logging.getLogger(__name__)


class AuthorityLevel(IntEnum):
    """Authority tiers in the leadership hierarchy."""

    SUPREME = 1  # Denauld Brown
    AI_CORE = 2  # M.E.L.
    EXECUTIVE = 3  # Courtney Sellars, Alexandra Martinez
    STRATEGIC = 4  # Marcus Sterling, Darius Washington
    ADVISORY = 5  # Bill McKenzie, Patricia Williams
    INNOVATION = 6  # David Kim, Rachel Foster, Jake Morrison, Maya Patel


@dataclass
class AuthorityPermissions:
    """Permissions for different authority operations."""

    code_changes: bool = False
    hiring: bool = False
    budget: bool = False
    strategy: bool = False
    final_approval_required: bool = True
    can_be_replaced: bool = True


class TierAuthority:
    """
    Manages authority validation and enforcement for the leadership hierarchy.

    This class ensures that only authorized bots can perform specific actions,
    validates emergency priorities, and enforces the approval chain requiring
    Denauld Brown's final approval for code changes.

    Attributes:
        bot_id: Unique identifier for the bot
        tier_level: Authority tier (1-6)
        emergency_priority: Emergency succession priority number
        permissions: AuthorityPermissions object defining what the bot can do

    Example:
        >>> authority = TierAuthority(
        ...     bot_id="denauld_brown",
        ...     tier_level=AuthorityLevel.SUPREME,
        ...     emergency_priority=1
        ... )
        >>> authority.validate_authority("code_changes")
        True
        >>> authority.requires_higher_approval("strategic_decision")
        False
    """

    # Denauld Brown's special status
    SUPREME_AUTHORITY_ID = "denauld_brown"

    def __init__(
        self,
        bot_id: str,
        tier_level: AuthorityLevel | int,
        emergency_priority: int,
        permissions: AuthorityPermissions | None = None,
    ) -> None:
        """
        Initialize TierAuthority.

        Args:
            bot_id: Unique identifier for the bot
            tier_level: Authority tier (1-6)
            emergency_priority: Emergency succession priority
            permissions: Optional custom permissions (auto-generated if None)
        """
        self.bot_id = bot_id
        self.tier_level = AuthorityLevel(tier_level) if isinstance(tier_level, int) else tier_level
        self.emergency_priority = emergency_priority
        self.permissions = permissions or self._generate_permissions()

        logger.info(f"Initialized TierAuthority for {bot_id} at tier {self.tier_level}")

    def _generate_permissions(self) -> AuthorityPermissions:
        """
        Generate default permissions based on tier level.

        Returns:
            AuthorityPermissions object with appropriate permissions
        """
        if self.bot_id == self.SUPREME_AUTHORITY_ID:
            return AuthorityPermissions(
                code_changes=True,
                hiring=True,
                budget=True,
                strategy=True,
                final_approval_required=False,  # Denauld IS final approval
                can_be_replaced=False,
            )

        # Tier-based permissions
        tier_permissions = {
            AuthorityLevel.AI_CORE: AuthorityPermissions(
                code_changes=True, hiring=False, budget=False, strategy=True, can_be_replaced=True
            ),
            AuthorityLevel.EXECUTIVE: AuthorityPermissions(
                code_changes=True, hiring=True, budget=True, strategy=True, can_be_replaced=True
            ),
            AuthorityLevel.STRATEGIC: AuthorityPermissions(
                code_changes=True, hiring=True, budget=False, strategy=True, can_be_replaced=True
            ),
            AuthorityLevel.ADVISORY: AuthorityPermissions(
                code_changes=False, hiring=False, budget=False, strategy=False, can_be_replaced=True
            ),
            AuthorityLevel.INNOVATION: AuthorityPermissions(
                code_changes=True, hiring=False, budget=False, strategy=False, can_be_replaced=True
            ),
        }

        return tier_permissions.get(self.tier_level, AuthorityPermissions())

    def validate_authority(self, action: str) -> bool:
        """
        Validate if the bot has authority to perform an action.

        Args:
            action: Action to validate (e.g., "code_changes", "hiring")

        Returns:
            True if authorized, False otherwise

        Example:
            >>> authority = TierAuthority("rachel_foster", AuthorityLevel.INNOVATION, 14)
            >>> authority.validate_authority("code_changes")
            True
            >>> authority.validate_authority("budget")
            False
        """
        if not hasattr(self.permissions, action):
            logger.warning(f"Unknown action '{action}' requested by {self.bot_id}")
            return False

        authorized = getattr(self.permissions, action)
        logger.debug(f"{self.bot_id} authority check for '{action}': {authorized}")

        return authorized

    def check_emergency_priority(self, other_priorities: Sequence[int]) -> bool:
        """
        Check if this bot has higher emergency priority than others.

        Lower priority number = higher priority (1 is highest).

        Args:
            other_priorities: List of other emergency priority numbers

        Returns:
            True if this bot has the highest priority

        Example:
            >>> authority = TierAuthority("denauld_brown", AuthorityLevel.SUPREME, 1)
            >>> authority.check_emergency_priority([2, 3, 14])
            True
        """
        if not other_priorities:
            return True

        has_highest = self.emergency_priority < min(other_priorities)
        logger.info(
            f"{self.bot_id} (priority {self.emergency_priority}) "
            f"emergency check vs {other_priorities}: {has_highest}"
        )

        return has_highest

    def enforce_approval_chain(self, action: str) -> bool:
        """
        Determine if an action requires Denauld Brown's approval.

        All code changes require final approval from Denauld Brown,
        regardless of tier level.

        Args:
            action: Action being performed

        Returns:
            True if Denauld's approval is required

        Example:
            >>> authority = TierAuthority("jake_morrison", AuthorityLevel.INNOVATION, 15)
            >>> authority.enforce_approval_chain("code_changes")
            True  # Requires Denauld's approval
        """
        # Denauld never requires his own approval
        if self.bot_id == self.SUPREME_AUTHORITY_ID:
            return False

        # Code changes ALWAYS require Denauld's approval
        if action == "code_changes":
            logger.info(f"{self.bot_id} code change requires Denauld Brown's approval")
            return True

        # Strategic decisions from tiers 4+ require approval
        if action == "strategy" and self.tier_level >= AuthorityLevel.STRATEGIC:
            return True

        # High-impact actions require approval
        high_impact_actions = ["hiring", "budget"]
        if action in high_impact_actions and self.permissions.final_approval_required:
            return True

        return False

    def requires_higher_approval(self, decision_type: str) -> bool:
        """
        Check if a decision requires escalation to a higher tier.

        Args:
            decision_type: Type of decision being made

        Returns:
            True if escalation required

        Example:
            >>> authority = TierAuthority("patricia_williams", AuthorityLevel.ADVISORY, 12)
            >>> authority.requires_higher_approval("code_changes")
            True  # Advisory tier cannot approve code changes alone
        """
        if self.bot_id == self.SUPREME_AUTHORITY_ID:
            return False  # Supreme authority never needs escalation

        # Map decision types to minimum required tiers
        decision_tier_requirements = {
            "code_changes": AuthorityLevel.INNOVATION,  # Innovation+ can propose
            "strategic_decision": AuthorityLevel.STRATEGIC,
            "hiring": AuthorityLevel.EXECUTIVE,
            "budget": AuthorityLevel.EXECUTIVE,
            "emergency": AuthorityLevel.AI_CORE,
        }

        required_tier = decision_tier_requirements.get(decision_type, AuthorityLevel.SUPREME)

        needs_escalation = self.tier_level > required_tier
        if needs_escalation:
            logger.info(f"{self.bot_id} (tier {self.tier_level}) requires escalation for {decision_type}")

        return needs_escalation

    def can_override_decision(self, other_authority: TierAuthority) -> bool:
        """
        Check if this authority can override another's decision.

        Args:
            other_authority: The other TierAuthority to compare against

        Returns:
            True if this authority can override the other

        Example:
            >>> denauld = TierAuthority("denauld_brown", AuthorityLevel.SUPREME, 1)
            >>> mel = TierAuthority("mel_digital_twin", AuthorityLevel.AI_CORE, 2)
            >>> denauld.can_override_decision(mel)
            True
            >>> mel.can_override_decision(denauld)
            False
        """
        # Denauld can override anyone
        if self.bot_id == self.SUPREME_AUTHORITY_ID:
            return True

        # No one can override Denauld
        if other_authority.bot_id == self.SUPREME_AUTHORITY_ID:
            return False

        # Lower tier number = higher authority
        can_override = self.tier_level < other_authority.tier_level

        logger.debug(
            f"{self.bot_id} (tier {self.tier_level}) "
            f"can override {other_authority.bot_id} (tier {other_authority.tier_level}): {can_override}"
        )

        return can_override

    def __repr__(self) -> str:
        """String representation of TierAuthority."""
        return (
            f"TierAuthority(bot_id='{self.bot_id}', "
            f"tier={self.tier_level.name}, "
            f"emergency_priority={self.emergency_priority})"
        )
