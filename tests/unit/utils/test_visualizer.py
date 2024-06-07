from tests.mocks.mock_prompt_driver import MockPromptDriver
from griptape.utils import WorkflowVisualizer
from griptape.tasks import PromptTask
from griptape.structures import Workflow


class TestWorkflowVisualizer:
    def test_visualize(self):
        workflow = Workflow(
            prompt_driver=MockPromptDriver(),
            tasks=[
                PromptTask("test1", id="task1"),
                PromptTask("test2", id="task2", parent_ids=["task1"]),
                PromptTask("test3", id="task3", parent_ids=["task1"]),
                PromptTask("test4", id="task4", parent_ids=["task2", "task3"]),
            ],
        )

        visualizer = WorkflowVisualizer(workflow)
        result = visualizer.render()

        assert (
            result
            == "https://mermaid.ink/img/Z3JhcGggTFI7Cgl0YXNrMS0tPiB0YXNrMiAmIHRhc2szOwoJdGFzazItLT4gdGFzazQ7Cgl0YXNrMy0tPiB0YXNrNDs="
        )
