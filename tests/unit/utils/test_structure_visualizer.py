from tests.mocks.mock_prompt_driver import MockPromptDriver
from griptape.utils import StructureVisualizer
from griptape.tasks import PromptTask
from griptape.structures import Agent, Workflow, Pipeline


class TestStructureVisualizer:
    def test_agent(self):
        agent = Agent(prompt_driver=MockPromptDriver(), tasks=[PromptTask("test1", id="task1")])

        visualizer = StructureVisualizer(agent)
        result = visualizer.to_url()

        assert result == "https://mermaid.ink/svg/Z3JhcGggVEQ7CgkndGFzazEnOw=="

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
            == "https://mermaid.ink/svg/Z3JhcGggVEQ7CgkndGFzazEnLS0+ICd0YXNrMic7CgkndGFzazInLS0+ICd0YXNrMyc7CgkndGFzazMnLS0+ICd0YXNrNCc7CgkndGFzazQnOw=="
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
            == "https://mermaid.ink/svg/Z3JhcGggVEQ7CgkndGFzazEnLS0+ICd0YXNrMicgJiAndGFzazMnOwoJJ3Rhc2syJy0tPiAndGFzazQnOwoJJ3Rhc2szJy0tPiAndGFzazQnOwoJJ3Rhc2s0Jzs="
        )
