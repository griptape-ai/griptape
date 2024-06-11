from tests.mocks.mock_prompt_driver import MockPromptDriver
from griptape.utils import StructureVisualizer
from griptape.tasks import PromptTask
from griptape.structures import Agent, Workflow, Pipeline


class TestStructureVisualizer:
    def test_agent(self):
        agent = Agent(prompt_driver=MockPromptDriver(), tasks=[PromptTask("test1", id="task1")])

        visualizer = StructureVisualizer(agent)
        result = visualizer.to_url()

        assert result == "https://mermaid.ink/svg/Z3JhcGggVEQ7Cgl0YXNrMTs="

    def test_pipeline(self):
        pipeline = Pipeline(
            prompt_driver=MockPromptDriver(),
            tasks=[
                PromptTask("test1", id="task1"),
                PromptTask("test2", id="task2"),
                PromptTask("test3", id="task3"),
                PromptTask("test4", id="task4"),
            ],
        )

        visualizer = StructureVisualizer(pipeline)
        result = visualizer.to_url()

        assert (
            result
            == "https://mermaid.ink/svg/Z3JhcGggVEQ7Cgl0YXNrMS0tPiB0YXNrMjsKCXRhc2syLS0+IHRhc2szOwoJdGFzazMtLT4gdGFzazQ7Cgl0YXNrNDs="
        )

    def test_workflow(self):
        workflow = Workflow(
            prompt_driver=MockPromptDriver(),
            tasks=[
                PromptTask("test1", id="task1"),
                PromptTask("test2", id="task2", parent_ids=["task1"]),
                PromptTask("test3", id="task3", parent_ids=["task1"]),
                PromptTask("test4", id="task4", parent_ids=["task2", "task3"]),
            ],
        )

        visualizer = StructureVisualizer(workflow)
        result = visualizer.to_url()

        assert (
            result
            == "https://mermaid.ink/svg/Z3JhcGggVEQ7Cgl0YXNrMS0tPiB0YXNrMiAmIHRhc2szOwoJdGFzazItLT4gdGFzazQ7Cgl0YXNrMy0tPiB0YXNrNDsKCXRhc2s0Ow=="
        )
