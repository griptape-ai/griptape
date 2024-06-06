from tests.utils.structure_tester import StructureTester
import pytest


class TestToolkitTask:
    @pytest.fixture(
        autouse=True,
        params=StructureTester.TOOLKIT_TASK_CAPABLE_PROMPT_DRIVERS,
        ids=StructureTester.prompt_driver_id_fn,
    )
    def structure_tester(self, request):
        import os
        from griptape.structures import Agent
        from griptape.tools import WebScraper, WebSearch, TaskMemoryClient

        return StructureTester(
            Agent(
                tools=[
                    WebSearch(
                        google_api_key=os.environ["GOOGLE_API_KEY"],
                        google_api_search_id=os.environ["GOOGLE_API_SEARCH_ID"],
                    ),
                    WebScraper(off_prompt=True),
                    TaskMemoryClient(off_prompt=False),
                ],
                conversation_memory=None,
                prompt_driver=request.param,
            )
        )

    def test_toolkit_task(self, structure_tester):
        structure_tester.run("Give me a summary of the top 2 search results about parrot facts.")
