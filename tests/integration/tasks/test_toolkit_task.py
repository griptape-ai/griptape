from tests.utils.structure_runner import StructureRunner
import pytest


class TestToolkitTask:
    @pytest.fixture(
        autouse=True,
        params=StructureRunner.TOOLKIT_TASK_CAPABLE_PROMPT_DRIVERS,
        ids=StructureRunner.prompt_driver_id_fn,
    )
    def structure_runner(self, request):
        import os
        from griptape.structures import Agent
        from griptape.tools import WebScraper, WebSearch, TaskMemoryClient

        return Agent(
            tools=[
                WebSearch(
                    google_api_key=os.environ["GOOGLE_API_KEY"],
                    google_api_search_id=os.environ["GOOGLE_API_SEARCH_ID"],
                    off_prompt=False,
                ),
                WebScraper(off_prompt=True),
                TaskMemoryClient(off_prompt=False),
            ],
            conversation_memory=None,
            prompt_driver=request.param,
        )

    def test_multi_step_cot(self, structure_runner):
        structure_runner.run_structure("Give me a summary of the top 2 search results about parrot facts.")
