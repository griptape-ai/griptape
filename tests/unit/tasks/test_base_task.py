from griptape.tasks import BaseTask, PromptTask, ActionSubtask, ExtractionTask, TextSummaryTask, ToolTask, ToolkitTask, TextQueryTask
from tests.mocks.mock_task import MockTask

class TestBaseTask:
    def test_init(self):
        task = MockTask(
            id="foo",
            type="foo",
            parent_ids=["foo"],
            child_ids=["bar"],
        )

        assert task.id == "foo"
        assert task.type == "foo"
        assert task.parent_ids == ["foo"]
        assert task.child_ids == ["bar"]
        assert task.structure is None

        
    def test_prompt_task_from_dict(self):
        dict_value = {
            "type": "PromptTask",
        }
        
        artifact = BaseTask.from_dict(dict_value)

        assert isinstance(artifact, PromptTask)
        assert artifact.output == "foo"

    def test_action_subtask_from_dict(self):
        dict_value = {
            "type": "ActionSubtask",
            "parent_task_id": "foo",
            "thought": "foo",
            "action_type": "foo",
            "action_name": "foo",
            "action_activity": "foo",
            "action_input": "foo",
        }
        
        artifact = BaseTask.from_dict(dict_value)

        assert isinstance(artifact, ActionSubtask)
        assert artifact.parent_task_id == "foo"
        assert artifact.thought == "foo"
        assert artifact.action_type == "foo"
        assert artifact.action_name == "foo"
        assert artifact.action_activity == "foo"
        assert artifact.action_input == "foo"

    def test_extraction_task_from_dict(self):
        dict_value = {
            "type": "ExtractionTask",
            "args": {
                "foo": "bar",
            },
        }
        
        artifact = BaseTask.from_dict(dict_value)

        assert isinstance(artifact, ExtractionTask)   
        
    def test_text_summary_task_from_dict(self):
        dict_value = {
            "type": "TextSummaryTask",
            "args": {
                "foo": "bar",
            },
        }
        
        artifact = BaseTask.from_dict(dict_value)

        assert isinstance(artifact, TextSummaryTask)

    def test_tool_task_from_dict(self):
        dict_value = {
            "type": "ToolTask",
            "args": {
                "foo": "bar",
            },
        }
        
        artifact = BaseTask.from_dict(dict_value)

        assert isinstance(artifact, ToolTask)

    def test_toolkit_task_from_dict(self):
        dict_value = {
            "type": "ToolkitTask",
            "args": {
                "foo": "bar",
            },
        }
        
        artifact = BaseTask.from_dict(dict_value)

        assert isinstance(artifact, ToolkitTask)


    def test_text_query_task_from_dict(self):
        dict_value = {
            "type": "TextQueryTask",
            "args": {
                "foo": "bar",
            },
        }
        
        artifact = BaseTask.from_dict(dict_value)

        assert isinstance(artifact, TextQueryTask)
