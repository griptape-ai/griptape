from tests.utils.structure_runner import run_structure, OUTPUT_RULESET, PROMPT_DRIVERS, prompt_driver_id_fn
import pytest


class TestFileManager:
    @pytest.fixture(autouse=True, params=PROMPT_DRIVERS, ids=prompt_driver_id_fn)
    def agent(self):
        from griptape.structures import Agent
        from griptape.tools import FileManager

        return Agent(
            tools=[FileManager()],
            rulesets=[OUTPUT_RULESET],
        )

    def test_save_content_to_disk(self, agent):
        result = run_structure(agent, 'Write the content "Hello World!" to a file called "poem.txt".')

        assert result["task_result"] == "success"

        result = run_structure(agent, 'Write the content "Hello World!" to a file called ".".')

        assert result["task_result"] == "failure"

    def test_load_files_from_disk(self, agent):
        result = run_structure(agent, "Read the content of the file called 'poem.txt'.")

        assert result["task_output"] == "Hello World!"
        assert result["task_result"] == "success"
