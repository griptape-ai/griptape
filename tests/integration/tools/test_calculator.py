from tests.utils.structure_runner import run_structure, OUTPUT_RULESET
import pytest


class TestCalculator:
    @pytest.fixture(autouse=True)
    def agent(self):
        from griptape.structures import Agent
        from griptape.tools import Calculator

        return Agent(
            tools=[Calculator()],
            rulesets=[OUTPUT_RULESET],
        )

    def test_calculate(self, agent):
        result = run_structure(agent, "What is 10 raised to the power of 5?")

        assert result["task_output"] == "100000"
        assert result["task_result"] == "success"
        
        result = run_structure(agent, "Multiply 7 times 3, then divide by 5 and add 10.")

        assert result["task_output"] == "14.2"
        assert result["task_result"] == "success"
        
        result = run_structure(agent, "What is 1 divided by 0?")

        assert result["task_result"] == "failure"
