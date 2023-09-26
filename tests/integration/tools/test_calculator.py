from tests.utils.structure_runner import run_structure, OUTPUT_RULESET, PROMPT_DRIVERS, prompt_driver_id_fn
import pytest


class TestCalculator:
    @pytest.fixture(autouse=True, params=PROMPT_DRIVERS, ids=prompt_driver_id_fn)
    def agent(self, request):
        from griptape.structures import Agent
        from griptape.tools import Calculator

        return Agent(
            tools=[Calculator()],
            prompt_driver=request.param,
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

        if result["task_result"] == "success":
            assert result["task_output"] == "Infinity"
        else:
            assert result["task_result"] == "failure"
