import pytest

from tests.utils.structure_tester import StructureTester


class TestPromptTask:
    @pytest.fixture(
        autouse=True,
        params=StructureTester.TOOLKIT_TASK_CAPABLE_PROMPT_DRIVERS,
        ids=StructureTester.generate_prompt_driver_id,
    )
    def structure_tester(self, request):
        import os

        from griptape.drivers.web_search.google import GoogleWebSearchDriver
        from griptape.structures import Agent
        from griptape.tools import PromptSummaryTool, WebScraperTool, WebSearchTool

        return StructureTester(
            Agent(
                tools=[
                    WebSearchTool(
                        web_search_driver=GoogleWebSearchDriver(
                            api_key=os.environ["GOOGLE_API_KEY"], search_id=os.environ["GOOGLE_API_SEARCH_ID"]
                        )
                    ),
                    WebScraperTool(off_prompt=True),
                    PromptSummaryTool(off_prompt=False),
                ],
                conversation_memory=None,
                prompt_driver=request.param,
            )
        )

    def test_toolkit_task(self, structure_tester):
        structure_tester.run("Give me a summary of the top 2 search results about parrot facts.")
