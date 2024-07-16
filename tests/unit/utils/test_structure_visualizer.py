from griptape.structures import Agent, Pipeline, Workflow
from griptape.tasks import PromptTask
from griptape.utils import StructureVisualizer
from tests.mocks.mock_prompt_driver import MockPromptDriver


class TestStructureVisualizer:
    def test_agent(self):
        agent = Agent(prompt_driver=MockPromptDriver(), tasks=[PromptTask("test1", id="task1")])

        visualizer = StructureVisualizer(agent)
        result = visualizer.to_url()

        assert result == "https://mermaid.ink/svg/Z3JhcGggVEQ7CgljYzVkYWYyNih0YXNrMSk7"

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
            == "https://mermaid.ink/svg/Z3JhcGggVEQ7CgljYzVkYWYyNih0YXNrMSktLT4gYWE1ZGU4N2UodGFzazIpOwoJYWE1ZGU4N2UodGFzazIpLS0+IDUxZmViYjIxKHRhc2szKTsKCTUxZmViYjIxKHRhc2szKS0tPiBhN2JlMzY4Yih0YXNrNCk7CglhN2JlMzY4Yih0YXNrNCk7"
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
            == "https://mermaid.ink/svg/Z3JhcGggVEQ7CgljYzVkYWYyNih0YXNrMSktLT4gYWE1ZGU4N2UodGFzazIpICYgNTFmZWJiMjEodGFzazMpOwoJYWE1ZGU4N2UodGFzazIpLS0+IGE3YmUzNjhiKHRhc2s0KTsKCTUxZmViYjIxKHRhc2szKS0tPiBhN2JlMzY4Yih0YXNrNCk7CglhN2JlMzY4Yih0YXNrNCk7"
        )
