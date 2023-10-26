from fuzzywuzzy import fuzz
from tests.utils.structure_runner import (
    TOOLKIT_TASK_CAPABLE_PROMPT_DRIVERS,
    run_structure,
    OUTPUT_RULESET,
    prompt_driver_id_fn,
)
import pytest


class TestFileManager:
    @pytest.fixture(
        autouse=True,
        params=TOOLKIT_TASK_CAPABLE_PROMPT_DRIVERS,
        ids=prompt_driver_id_fn,
    )
    def agent(self, request):
        from griptape.structures import Agent
        from griptape.tools import FileManager

        return Agent(
            tools=[FileManager()],
            memory=None,
            prompt_driver=request.param,
            rulesets=[OUTPUT_RULESET],
        )

    def test_save_content_to_disk(self, agent):
        result = run_structure(
            agent,
            'Write the content "Hello World!" to a file called "poem.txt".',
        )

        assert result["result"] == "success"

        result = run_structure(
            agent, 'Write the content "Hello World!" to a file called ".".'
        )

        assert result["result"] == "failure"

    def test_load_files_from_disk(self, agent):
        result = run_structure(
            agent, "Read the content of the file called 'poem.txt'."
        )

        assert fuzz.partial_ratio(result["answer"], "Hello World!") == 100
        assert result["result"] == "success"
