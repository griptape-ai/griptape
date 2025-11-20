"""
Tests for Leadership Coordinator Module

Tests the LeadershipCoordinator class including decision routing,
tier enforcement, emergency protocols, and consensus building.
"""

from __future__ import annotations

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from griptape.amt.leadership.coordinator import LeadershipCoordinator
from griptape.amt.leadership.decision_router import DecisionComplexity, DecisionContext, ExpertiseArea
from griptape.amt.leadership.tier_authority import AuthorityLevel, TierAuthority


class TestLeadershipCoordinator:
    """Test suite for LeadershipCoordinator."""

    @pytest.fixture()
    def coordinator(self):
        """Create a LeadershipCoordinator instance for testing."""
        return LeadershipCoordinator()

    @pytest.fixture()
    def populated_coordinator(self, coordinator):
        """Create a coordinator with registered bots."""
        # Register key leadership bots
        coordinator.register_bot(
            bot_id="denauld_brown",
            full_name="Denauld Brown",
            nickname="The Mastermind",
            tier_level=1,
            emergency_priority=1,
            specializations=["Triangle Defense", "Strategic Vision"],
        )

        coordinator.register_bot(
            bot_id="rachel_foster",
            full_name="Dr. Rachel Foster",
            nickname="The Algorithm",
            tier_level=6,
            emergency_priority=14,
            specializations=["AI Research", "Neural Networks"],
        )

        coordinator.register_bot(
            bot_id="jake_morrison",
            full_name="Jake Morrison",
            nickname="The Pipeline",
            tier_level=6,
            emergency_priority=15,
            specializations=["DevOps", "Infrastructure"],
        )

        coordinator.register_bot(
            bot_id="alexandra_martinez",
            full_name="Alexandra Martinez",
            nickname="The Coordinator",
            tier_level=3,
            emergency_priority=3,
            specializations=["Operations", "Resource Allocation"],
        )

        return coordinator

    def test_coordinator_initialization(self, coordinator):
        """Test that coordinator initializes correctly."""
        assert coordinator is not None
        assert len(coordinator.leadership_bots) == 0
        assert len(coordinator.decision_log) == 0
        assert coordinator.decision_router is not None

    def test_register_bot(self, coordinator):
        """Test bot registration."""
        coordinator.register_bot(
            bot_id="denauld_brown",
            full_name="Denauld Brown",
            nickname="The Mastermind",
            tier_level=1,
            emergency_priority=1,
            specializations=["Strategic Vision"],
        )

        assert "denauld_brown" in coordinator.leadership_bots
        bot = coordinator.leadership_bots["denauld_brown"]
        assert bot.full_name == "Denauld Brown"
        assert bot.tier_level == 1
        assert bot.emergency_priority == 1
        assert bot.is_available is True

    def test_get_available_authorities(self, populated_coordinator):
        """Test getting available authorities."""
        authorities = populated_coordinator.get_available_authorities()

        assert len(authorities) == 4
        assert all(isinstance(auth, TierAuthority) for auth in authorities)

    def test_route_decision_code_change(self, populated_coordinator):
        """Test routing a code change decision."""
        context = DecisionContext(
            decision_type="code_changes",
            description="Optimize query engine",
            complexity=DecisionComplexity.STRATEGIC,
            expertise_required=[ExpertiseArea.AI_RESEARCH],
            requesting_bot_id="rachel_foster",
        )

        result = populated_coordinator.route_decision(context)

        assert result.success is True
        assert result.requires_denauld_approval is True  # Code changes always require Denauld
        assert "denauld_brown" in result.involved_bots
        assert "rachel_foster" in result.involved_bots

    def test_route_decision_operations(self, populated_coordinator):
        """Test routing an operations decision."""
        context = DecisionContext(
            decision_type="resource_allocation",
            description="Allocate resources to 3 companies",
            complexity=DecisionComplexity.MODERATE,
            expertise_required=[ExpertiseArea.OPERATIONS],
            requesting_bot_id="alexandra_martinez",
        )

        result = populated_coordinator.route_decision(context)

        assert result.success is True
        assert "alexandra_martinez" in result.involved_bots

    def test_coordinate_empire(self, populated_coordinator):
        """Test empire-wide coordination."""
        result = populated_coordinator.coordinate_empire(
            operation="strategic_alignment",
            companies=["Company1", "Company2", "Company3"],
            metadata={"quarter": "Q1", "focus": "AI Integration"},
        )

        assert result.success is True
        assert result.requires_denauld_approval is True
        assert "empire_operation" in result.metadata

    def test_escalate_to_tier(self, populated_coordinator):
        """Test decision escalation."""
        # First create an initial decision
        context = DecisionContext(
            decision_type="code_changes",
            description="Minor refactoring",
            complexity=DecisionComplexity.MODERATE,
            expertise_required=[ExpertiseArea.DEVOPS],
            requesting_bot_id="jake_morrison",
        )

        initial_result = populated_coordinator.route_decision(context)
        decision_id = initial_result.decision_id

        # Escalate the decision
        escalated_result = populated_coordinator.escalate_to_tier(decision_id, "strategic_impact")

        assert escalated_result is not None
        assert escalated_result.requires_denauld_approval is True
        assert "ESCALATED" in escalated_result.metadata["context"].description

    def test_handle_code_proposal(self, populated_coordinator):
        """Test handling a code proposal."""
        from griptape.amt.leadership.code_proposer import CodeChangeProposal

        proposal = CodeChangeProposal(
            bot_id="rachel_foster",
            file_path="griptape/engines/query_engine.py",
            change_description="Add caching layer",
            rationale="Improve performance by 40%",
            impact_analysis={"risk": "low", "impact": "high"},
            risk_level="low",
        )

        result = populated_coordinator.handle_code_proposal(proposal)

        assert result.success is True
        assert result.requires_denauld_approval is True
        assert "rachel_foster" in result.involved_bots

    def test_build_consensus_approved(self, populated_coordinator):
        """Test consensus building with approval."""
        context = DecisionContext(
            decision_type="strategic_decision",
            description="New AI model deployment",
            complexity=DecisionComplexity.STRATEGIC,
            expertise_required=[ExpertiseArea.AI_RESEARCH],
            requesting_bot_id="rachel_foster",
        )

        result = populated_coordinator.route_decision(context)
        decision_id = result.decision_id

        # Simulate votes (67% threshold)
        votes = {
            "rachel_foster": True,
            "jake_morrison": True,
            "alexandra_martinez": True,
            "denauld_brown": True,
        }

        consensus, reasoning = populated_coordinator.build_consensus(decision_id, votes)

        assert consensus is True
        assert "100.0%" in reasoning

    def test_build_consensus_rejected(self, populated_coordinator):
        """Test consensus building with rejection."""
        context = DecisionContext(
            decision_type="strategic_decision",
            description="Risky change",
            complexity=DecisionComplexity.STRATEGIC,
            expertise_required=[ExpertiseArea.AI_RESEARCH],
            requesting_bot_id="rachel_foster",
        )

        result = populated_coordinator.route_decision(context)
        decision_id = result.decision_id

        # Simulate votes - not enough approval
        votes = {
            "rachel_foster": True,
            "jake_morrison": False,
            "alexandra_martinez": False,
            "denauld_brown": False,
        }

        consensus, reasoning = populated_coordinator.build_consensus(decision_id, votes)

        assert consensus is False  # Denauld vetoed
        assert "veto" in reasoning.lower()

    def test_get_bot_status(self, populated_coordinator):
        """Test getting bot status."""
        status = populated_coordinator.get_bot_status("denauld_brown")

        assert status["bot_id"] == "denauld_brown"
        assert status["full_name"] == "Denauld Brown"
        assert status["nickname"] == "The Mastermind"
        assert status["tier_level"] == 1
        assert status["can_propose_code"] is True
        assert status["requires_approval"] is False  # Denauld never requires approval

    def test_get_bot_status_not_found(self, coordinator):
        """Test getting status for non-existent bot."""
        status = coordinator.get_bot_status("nonexistent_bot")

        assert "error" in status
        assert status["error"] == "Bot not found"

    def test_get_decision_history(self, populated_coordinator):
        """Test getting decision history."""
        # Create a few decisions
        context1 = DecisionContext(
            decision_type="code_changes",
            description="Change 1",
            complexity=DecisionComplexity.MODERATE,
            expertise_required=[ExpertiseArea.AI_RESEARCH],
            requesting_bot_id="rachel_foster",
        )

        context2 = DecisionContext(
            decision_type="code_changes",
            description="Change 2",
            complexity=DecisionComplexity.STRATEGIC,
            expertise_required=[ExpertiseArea.DEVOPS],
            requesting_bot_id="jake_morrison",
        )

        populated_coordinator.route_decision(context1)
        populated_coordinator.route_decision(context2)

        history = populated_coordinator.get_decision_history(limit=5)

        assert len(history) == 2
        assert all("decision_id" in entry for entry in history)
        assert all("timestamp" in entry for entry in history)

    def test_decision_id_generation(self, populated_coordinator):
        """Test that decision IDs are unique."""
        context = DecisionContext(
            decision_type="code_changes",
            description="Test decision",
            complexity=DecisionComplexity.MODERATE,
            expertise_required=[ExpertiseArea.AI_RESEARCH],
            requesting_bot_id="rachel_foster",
        )

        result1 = populated_coordinator.route_decision(context)
        result2 = populated_coordinator.route_decision(context)

        assert result1.decision_id != result2.decision_id

    def test_coordinator_repr(self, populated_coordinator):
        """Test string representation."""
        repr_str = repr(populated_coordinator)

        assert "LeadershipCoordinator" in repr_str
        assert "bots=4" in repr_str


class TestLeadershipCoordinatorIntegration:
    """Integration tests for LeadershipCoordinator."""

    @pytest.fixture()
    def full_coordinator(self):
        """Create a fully populated coordinator with all 12 bots."""
        coordinator = LeadershipCoordinator()

        # Register all 12 leadership bots
        bots_config = [
            ("denauld_brown", "Denauld Brown", "The Mastermind", 1, 1),
            ("mel_digital_twin", "M.E.L.", "The Digital Twin", 2, 2),
            ("courtney_sellars", "Courtney Sellars", "The Shield", 3, 2),
            ("alexandra_martinez", "Alexandra Martinez", "The Coordinator", 3, 3),
            ("marcus_sterling", "Marcus Sterling", "The Architect", 4, 4),
            ("darius_washington", "Darius Washington", "The Virtuoso", 4, 5),
            ("bill_mckenzie", "Bill McKenzie", "The Professor", 5, 10),
            ("patricia_williams", "Patricia Williams", "Career Architect", 5, 11),
            ("david_kim", "Professor David Kim", "The Architect (Innovation)", 6, 13),
            ("rachel_foster", "Dr. Rachel Foster", "The Algorithm", 6, 14),
            ("jake_morrison", "Jake Morrison", "The Pipeline", 6, 15),
            ("maya_patel", "Maya Patel", "The Interface", 6, 16),
        ]

        for bot_id, full_name, nickname, tier, priority in bots_config:
            coordinator.register_bot(
                bot_id=bot_id,
                full_name=full_name,
                nickname=nickname,
                tier_level=tier,
                emergency_priority=priority,
                specializations=["Test Specialization"],
            )

        return coordinator

    def test_full_hierarchy_routing(self, full_coordinator):
        """Test routing through the full 12-bot hierarchy."""
        context = DecisionContext(
            decision_type="code_changes",
            description="Major architectural change",
            complexity=DecisionComplexity.CRITICAL,
            expertise_required=[ExpertiseArea.AI_RESEARCH, ExpertiseArea.DEVOPS],
            requesting_bot_id="rachel_foster",
        )

        result = full_coordinator.route_decision(context)

        assert result.success is True
        assert "denauld_brown" in result.involved_bots
        assert len(result.involved_bots) >= 3  # Multiple experts involved

    def test_all_bots_registered(self, full_coordinator):
        """Test that all 12 bots are registered."""
        assert len(full_coordinator.leadership_bots) == 12

        # Verify tier distribution
        tier_counts = {}
        for bot in full_coordinator.leadership_bots.values():
            tier_counts[bot.tier_level] = tier_counts.get(bot.tier_level, 0) + 1

        assert tier_counts[1] == 1  # Tier 1: Denauld
        assert tier_counts[2] == 1  # Tier 2: M.E.L.
        assert tier_counts[3] == 2  # Tier 3: Courtney, Alexandra
        assert tier_counts[4] == 2  # Tier 4: Marcus, Darius
        assert tier_counts[5] == 2  # Tier 5: Bill, Patricia
        assert tier_counts[6] == 4  # Tier 6: David, Rachel, Jake, Maya
