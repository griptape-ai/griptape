from fuzzywuzzy import fuzz
from tests.utils.structure_runner import (
    PROMPT_TASK_CAPABLE_PROMPT_DRIVERS,
    run_structure,
    OUTPUT_RULESET,
    prompt_driver_id_fn,
)
import pytest


class TestPromptTask:
    @pytest.fixture(
        autouse=True,
        params=PROMPT_TASK_CAPABLE_PROMPT_DRIVERS,
        ids=prompt_driver_id_fn,
    )
    def agent(self, request):
        from griptape.structures import Agent

        return Agent(
            memory=None, prompt_driver=request.param, rulesets=[OUTPUT_RULESET]
        )

    def test_prompt_task(self, agent):
        result = run_structure(
            agent,
            "Write a haiku about pirates. It must contain the word 'ship'.",
        )

        assert fuzz.partial_ratio(result["answer"], "ship") >= 95
