from griptape.core.drivers import OpenAiPromptDriver
from griptape.rules import Rule
from griptape.tokenizers import TiktokenTokenizer
from griptape.tasks import PromptTask, ToolkitTask
from griptape.structures import Workflow
from griptape.schemas import WorkflowSchema


class TestWorkflowSchema:
    def test_serialization(self):
        workflow = Workflow(
            prompt_driver=OpenAiPromptDriver(
                tokenizer=TiktokenTokenizer(stop_sequence="<test>"),
                temperature=0.12345
            ),
            rules=[
                Rule("test rule 1"),
                Rule("test rule 2"),
            ]
        )

        tools = [
            "calculator",
            "google_search"
        ]

        workflow.add_tasks(
            PromptTask("test prompt"),
            ToolkitTask("test tool prompt", tool_names=["calculator"])
        )

        task = ToolkitTask("test router task", tool_names=tools)

        workflow.tasks[0].add_child(task)
        workflow.tasks[1].add_child(task)

        workflow_dict = WorkflowSchema().dump(workflow)

        assert len(workflow_dict["tasks"]) == 3
        assert len(workflow_dict["rules"]) == 2
        assert workflow_dict["tasks"][0]["state"] == "PENDING"
        assert workflow_dict["tasks"][0]["child_ids"][0] == task.id
        assert workflow.tasks[0].id in task.parent_ids
        assert workflow.tasks[1].id in task.parent_ids
        assert len(workflow_dict["tasks"][-1]["tool_names"]) == 2
        assert workflow_dict["prompt_driver"]["temperature"] == 0.12345
        assert workflow_dict["prompt_driver"]["tokenizer"]["stop_sequence"] == "<test>"
        assert workflow_dict["rules"][0]["value"] == "test rule 1"

    def test_deserialization(self):
        workflow = Workflow(
            prompt_driver=OpenAiPromptDriver(
                tokenizer=TiktokenTokenizer(stop_sequence="<test>"),
                temperature=0.12345
            ),
            rules=[
                Rule("test rule 1"),
                Rule("test rule 2"),
            ]
        )

        tools = [
            "calculator",
            "google_search"
        ]

        workflow.add_tasks(
            PromptTask("test prompt"),
            ToolkitTask("test tool prompt", tool_names=["calculator"])
        )

        task = ToolkitTask("test router task", tool_names=tools)

        workflow.tasks[0].add_child(task)
        workflow.tasks[1].add_child(task)

        workflow_dict = WorkflowSchema().dump(workflow)
        deserialized_workflow = WorkflowSchema().load(workflow_dict)

        assert len(deserialized_workflow.tasks) == 3
        assert len(deserialized_workflow.rules) == 2
        assert deserialized_workflow.tasks[0].child_ids[0] == task.id
        assert deserialized_workflow.tasks[0].id in task.parent_ids
        assert deserialized_workflow.tasks[1].id in task.parent_ids
        assert len(deserialized_workflow.tasks[-1].tool_names) == 2
        assert deserialized_workflow.prompt_driver.temperature == 0.12345
        assert deserialized_workflow.prompt_driver.tokenizer.stop_sequence == "<test>"
        assert deserialized_workflow.rules[0].value == "test rule 1"
