from griptape.engines.summary.prompt_summary_engine import PromptSummaryEngine
from griptape.tasks import TextSummaryTask
from tests.utils.structure_runner import StructureRunner
import pytest


class TestSummaryTask:
    @pytest.fixture(
        autouse=True,
        params=StructureRunner.SUMMARY_TASK_CAPABLE_PROMPT_DRIVERS,
        ids=StructureRunner.prompt_driver_id_fn,
    )
    def structure_runner(self, request):
        from griptape.structures import Agent

        agent = Agent(conversation_memory=None, prompt_driver=request.param)
        agent.add_task(TextSummaryTask(summary_engine=PromptSummaryEngine(prompt_driver=request.param)))

        return StructureRunner(agent)

    def test_summary_task(self, structure_runner):
        structure_runner.run_structure(
            """
                Meeting transcriot: 
                Miguel: Hi Brant, I want to discuss the workstream  for our new product launch 
                Brant: Sure Miguel, is there anything in particular you want to discuss? 
                Miguel: Yes, I want to talk about how users enter into the product. 
                Brant: Ok, in that case let me add in Namita. 
                Namita: Hey everyone 
                Brant: Hi Namita, Miguel wants to discuss how users enter into the product. 
                Miguel: its too complicated and we should remove friction.  for example, why do I need to fill out additional forms?  I also find it difficult to find where to access the product when I first land on the landing page. 
                Brant: I would also add that I think there are too many steps. 
                Namita: Ok, I can work on the landing page to make the product more discoverable but brant can you work on the additional forms? 
                Brant: Yes but I would need to work with James from another team as he needs to unblock the sign up workflow.  Miguel can you document any other concerns so that I can discuss with James only once? 
                Miguel: Sure. 
        """
        )
