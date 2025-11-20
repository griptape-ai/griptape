"""
Tests for Code Proposer Module

Tests the CodeProposer class including codebase analysis, proposal creation,
GitHub integration, and approval workflow.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from griptape.amt.leadership.code_proposer import CodeChangeProposal, CodeProposer, PullRequestResult


class TestCodeProposer:
    """Test suite for CodeProposer."""

    @pytest.fixture()
    def proposer(self):
        """Create a CodeProposer instance for testing."""
        return CodeProposer(bot_id="rachel_foster", github_token="test_token_123")

    @pytest.fixture()
    def test_file(self, tmp_path):
        """Create a temporary test file."""
        test_file = tmp_path / "test_module.py"
        test_file.write_text(
            """
def example_function():
    '''Example function for testing.'''
    result = []
    for i in range(10):
        if i % 2 == 0:
            result.append(i)
    return result

class ExampleClass:
    def __init__(self):
        self.data = []

    def process(self):
        # TODO: Implement processing
        pass
"""
        )
        return test_file

    def test_proposer_initialization(self, proposer):
        """Test that proposer initializes correctly."""
        assert proposer.bot_id == "rachel_foster"
        assert proposer.github_token == "test_token_123"
        assert proposer.repo_name == "AnalyzeMyTeamHQ/analyzemyteam-griptape-core"
        assert proposer.base_branch == "main"

    def test_proposer_initialization_env_token(self, monkeypatch):
        """Test initialization with environment variable token."""
        monkeypatch.setenv("GITHUB_PAT", "env_token_456")
        proposer = CodeProposer(bot_id="jake_morrison")

        assert proposer.github_token == "env_token_456"

    def test_analyze_codebase_success(self, proposer, test_file):
        """Test successful codebase analysis."""
        analysis = proposer.analyze_codebase(test_file)

        assert analysis["exists"] is True
        assert analysis["lines_of_code"] > 0
        assert "complexity_score" in analysis
        assert "improvement_opportunities" in analysis
        assert isinstance(analysis["improvement_opportunities"], list)

    def test_analyze_codebase_file_not_found(self, proposer):
        """Test analysis of non-existent file."""
        analysis = proposer.analyze_codebase("/nonexistent/file.py")

        assert analysis["exists"] is False
        assert "error" in analysis

    def test_analyze_codebase_identifies_todos(self, proposer, test_file):
        """Test that analysis identifies TODO comments."""
        analysis = proposer.analyze_codebase(test_file)

        improvements = analysis["improvement_opportunities"]
        assert any("TODO" in imp for imp in improvements)

    def test_calculate_complexity(self, proposer):
        """Test complexity calculation."""
        simple_content = "x = 1\ny = 2\n"
        complex_content = """
def func1():
    if True:
        for i in range(10):
            if i > 5:
                while True:
                    try:
                        pass
                    except:
                        pass

class MyClass:
    def method1(self):
        pass

    def method2(self):
        pass
"""

        simple_complexity = proposer._calculate_complexity(simple_content)
        complex_complexity = proposer._calculate_complexity(complex_content)

        assert simple_complexity < complex_complexity
        assert 1 <= simple_complexity <= 10
        assert 1 <= complex_complexity <= 10

    def test_identify_improvements(self, proposer):
        """Test improvement identification."""
        content_with_issues = """
# TODO: Fix this
from package import *

""" + "\n".join(["def func():\n    pass\n" for _ in range(100)])

        improvements = proposer._identify_improvements(content_with_issues)

        assert len(improvements) > 0
        assert any("TODO" in imp for imp in improvements)
        assert any("wildcard" in imp for imp in improvements)

    def test_propose_change(self, proposer, test_file):
        """Test creating a code change proposal."""
        proposal = proposer.propose_change(
            file_path=test_file,
            change_description="Optimize loop performance",
            rationale="Reduce CPU usage by 30%",
            risk_level="low",
            estimated_impact="moderate",
        )

        assert isinstance(proposal, CodeChangeProposal)
        assert proposal.bot_id == "rachel_foster"
        assert proposal.change_description == "Optimize loop performance"
        assert proposal.risk_level == "low"
        assert proposal.estimated_impact == "moderate"
        assert "file_analysis" in proposal.impact_analysis
        assert proposal.created_at is not None

    def test_determine_testing_requirements(self, proposer):
        """Test testing requirements determination."""
        low_risk_tests = proposer._determine_testing_requirements("low")
        medium_risk_tests = proposer._determine_testing_requirements("medium")
        high_risk_tests = proposer._determine_testing_requirements("high")

        assert "unit_tests" in low_risk_tests
        assert len(low_risk_tests) == 1

        assert "unit_tests" in medium_risk_tests
        assert "integration_tests" in medium_risk_tests
        assert len(medium_risk_tests) == 2

        assert "unit_tests" in high_risk_tests
        assert "integration_tests" in high_risk_tests
        assert "system_tests" in high_risk_tests
        assert "manual_review" in high_risk_tests

    @patch("griptape.amt.leadership.code_proposer.Github")
    @patch("griptape.amt.leadership.code_proposer.Auth")
    def test_create_pull_request_success(self, mock_auth, mock_github, proposer, test_file):
        """Test successful pull request creation."""
        # Mock GitHub API
        mock_repo = MagicMock()
        mock_pr = MagicMock()
        mock_pr.number = 123
        mock_pr.html_url = "https://github.com/test/repo/pull/123"
        mock_pr.state = "open"
        mock_pr.merged = False
        mock_pr.created_at = None
        mock_pr.updated_at = None
        mock_pr.user.login = "rachel_foster"

        mock_repo.create_pull.return_value = mock_pr
        mock_repo.get_git_ref.return_value.object.sha = "abc123"

        mock_github_instance = MagicMock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github.return_value = mock_github_instance

        # Create proposal
        proposal = proposer.propose_change(
            file_path=test_file,
            change_description="Test change",
            rationale="Testing",
            risk_level="low",
        )

        # Create PR
        pr_result = proposer.create_pull_request(proposal)

        assert pr_result is not None
        assert isinstance(pr_result, PullRequestResult)
        assert pr_result.pr_number == 123
        assert pr_result.status == "pending_review"

    def test_create_pull_request_no_token(self):
        """Test PR creation without token."""
        proposer = CodeProposer(bot_id="test_bot", github_token=None)

        proposal = CodeChangeProposal(
            bot_id="test_bot",
            file_path="test.py",
            change_description="Test",
            rationale="Test",
            impact_analysis={},
        )

        result = proposer.create_pull_request(proposal)
        assert result is None

    def test_generate_pr_description(self, proposer, test_file):
        """Test PR description generation."""
        proposal = proposer.propose_change(
            file_path=test_file,
            change_description="Improve performance",
            rationale="Optimize algorithm",
            risk_level="medium",
        )

        description = proposer._generate_pr_description(proposal, code_diff="+ optimized code")

        assert "Improve performance" in description
        assert "Optimize algorithm" in description
        assert "medium" in description.lower()
        assert "rachel_foster" in description
        assert "denauld-brown" in description
        assert "optimized code" in description

    @patch("griptape.amt.leadership.code_proposer.Github")
    @patch("griptape.amt.leadership.code_proposer.Auth")
    def test_get_proposal_status(self, mock_auth, mock_github, proposer):
        """Test getting proposal status."""
        # Mock GitHub API
        mock_pr = MagicMock()
        mock_pr.number = 123
        mock_pr.state = "open"
        mock_pr.merged = False
        mock_pr.mergeable = True
        mock_pr.comments = 2

        mock_review = MagicMock()
        mock_review.user.login = "denauld_brown"
        mock_review.state = "APPROVED"
        mock_pr.get_reviews.return_value = [mock_review]

        mock_label = MagicMock()
        mock_label.name = "leadership-proposed"
        mock_pr.labels = [mock_label]

        mock_repo = MagicMock()
        mock_repo.get_pull.return_value = mock_pr

        mock_github_instance = MagicMock()
        mock_github_instance.get_repo.return_value = mock_repo
        mock_github.return_value = mock_github_instance

        # Get status
        status = proposer.get_proposal_status(123)

        assert status["pr_number"] == 123
        assert status["state"] == "open"
        assert status["merged"] is False
        assert len(status["reviews"]) == 1
        assert status["reviews"][0]["user"] == "denauld_brown"

    def test_proposer_repr(self, proposer):
        """Test string representation."""
        repr_str = repr(proposer)

        assert "CodeProposer" in repr_str
        assert "rachel_foster" in repr_str
        assert "AnalyzeMyTeamHQ" in repr_str


class TestCodeChangeProposal:
    """Test suite for CodeChangeProposal dataclass."""

    def test_proposal_creation(self):
        """Test creating a code change proposal."""
        proposal = CodeChangeProposal(
            bot_id="rachel_foster",
            file_path="test.py",
            change_description="Test change",
            rationale="Testing purposes",
            impact_analysis={"risk": "low"},
            risk_level="low",
            estimated_impact="minimal",
        )

        assert proposal.bot_id == "rachel_foster"
        assert proposal.file_path == "test.py"
        assert proposal.risk_level == "low"
        assert proposal.created_at is not None
        assert isinstance(proposal.testing_requirements, list)

    def test_proposal_default_values(self):
        """Test proposal with default values."""
        proposal = CodeChangeProposal(
            bot_id="test_bot",
            file_path="test.py",
            change_description="Test",
            rationale="Test",
            impact_analysis={},
        )

        assert proposal.risk_level == "medium"
        assert proposal.estimated_impact == "moderate"
        assert proposal.code_diff is None
        assert proposal.testing_requirements == []


class TestCodeProposerIntegration:
    """Integration tests for CodeProposer with real file operations."""

    @pytest.fixture()
    def integration_proposer(self, tmp_path):
        """Create proposer with temporary directory."""
        return CodeProposer(bot_id="integration_test", github_token="test_token")

    @pytest.fixture()
    def complex_file(self, tmp_path):
        """Create a complex test file."""
        file_path = tmp_path / "complex_module.py"
        file_path.write_text(
            """
'''Complex module for testing.'''

from typing import List, Dict, Any
import * from utils  # Bad practice

# TODO: Refactor this module
# FIXME: Fix error handling

class DataProcessor:
    '''Process data with multiple methods.'''

    def __init__(self):
        self.data = []

    def process(self, items: List[Any]) -> Dict[str, Any]:
        result = {}
        for item in items:
            try:
                if item:
                    for key in item:
                        if key:
                            try:
                                result[key] = item[key]
                            except Exception:
                                pass
            except Exception:
                pass
        return result

    def validate(self, data: Dict) -> bool:
        if data:
            for key in data:
                if key:
                    try:
                        if data[key]:
                            return True
                    except:
                        pass
        return False

def helper_function():
    pass

async def async_helper():
    pass
"""
        )
        return file_path

    def test_analyze_complex_file(self, integration_proposer, complex_file):
        """Test analysis of complex file."""
        analysis = integration_proposer.analyze_codebase(complex_file)

        assert analysis["exists"] is True
        assert analysis["complexity_score"] >= 3
        assert len(analysis["improvement_opportunities"]) > 0

        improvements = analysis["improvement_opportunities"]
        assert any("TODO" in imp for imp in improvements)
        assert any("wildcard" in imp for imp in improvements)

    def test_full_proposal_workflow(self, integration_proposer, complex_file):
        """Test complete proposal workflow."""
        # Step 1: Analyze codebase
        analysis = integration_proposer.analyze_codebase(complex_file)
        assert analysis["exists"] is True

        # Step 2: Create proposal
        proposal = integration_proposer.propose_change(
            file_path=complex_file,
            change_description="Refactor DataProcessor class",
            rationale="Reduce complexity and improve maintainability",
            risk_level="high",
            estimated_impact="significant",
        )

        assert proposal is not None
        assert proposal.risk_level == "high"
        assert "manual_review" in proposal.testing_requirements

        # Step 3: Verify impact analysis
        impact = proposal.impact_analysis
        assert "file_analysis" in impact
        assert impact["risk_level"] == "high"
        assert impact["proposing_bot"] == "integration_test"
