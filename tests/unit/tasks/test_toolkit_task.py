from tests.mocks.mock_tool.tool import MockTool
from griptape.artifacts import ErrorOutput
from griptape.tasks import ToolkitTask, ToolSubtask
from griptape.core import ToolLoader
from tests.mocks.mock_value_driver import MockValueDriver
from griptape.structures import Pipeline


class TestToolkitSubtask:
    def test_init(self):
        assert len(ToolkitTask("test", tool_names=["Calculator", "WebSearch"]).tool_names) == 2

        try:
            assert ToolkitTask("test", tool_names=["Calculator", "Calculator"])
        except ValueError:
            assert True

    def test_run(self):
        output = """Output: done"""

        tools = [
            MockTool(name="ToolOne"),
            MockTool(name="ToolTwo")
        ]

        task = ToolkitTask("test", tool_names=["ToolOne", "ToolTwo"])
        pipeline = Pipeline(
            prompt_driver=MockValueDriver(output),
            tool_loader=ToolLoader(tools=tools)
        )

        pipeline.add_task(task)

        result = pipeline.run()

        assert len(task.tools) == 2
        assert len(task._subtasks) == 1
        assert result.output.value == "done"
    
    def test_run_max_subtasks(self):
        output = """Action: {"tool": "test"}"""

        task = ToolkitTask("test", tool_names=["Calculator"], max_subtasks=3)
        pipeline = Pipeline(prompt_driver=MockValueDriver(output))

        pipeline.add_task(task)

        pipeline.run()

        assert len(task._subtasks) == 3
        assert isinstance(task.output, ErrorOutput)

    def test_init_from_prompt_1(self):
        valid_input = """Thought: need to test\nAction: {"tool": "test", "action": "test action", "value": "test input"}\nObservation: test 
        observation\nOutput: test output"""
        task = ToolkitTask("test", tool_names=["Calculator"])

        Pipeline().add_task(task)

        subtask = task.add_subtask(ToolSubtask(valid_input))

        assert subtask.thought == "need to test"
        assert subtask.tool_name == "test"
        assert subtask.tool_action == "test action"
        assert subtask.tool_value == "test input"
        assert subtask.output is None

    def test_init_from_prompt_2(self):
        valid_input = """Thought: need to test\nObservation: test 
        observation\nOutput: test output"""
        task = ToolkitTask("test", tool_names=["Calculator"])

        Pipeline().add_task(task)

        subtask = task.add_subtask(ToolSubtask(valid_input))

        assert subtask.thought == "need to test"
        assert subtask.tool_name is None
        assert subtask.tool_action is None
        assert subtask.tool_value is None
        assert subtask.output.value == "test output"

    def test_add_subtask(self):
        task = ToolkitTask("test", tool_names=["Calculator"])
        subtask1 = ToolSubtask("test1", tool_name="test", tool_action="test", tool_value="test")
        subtask2 = ToolSubtask("test2", tool_name="test", tool_action="test", tool_value="test")

        Pipeline().add_task(task)

        task.add_subtask(subtask1)
        task.add_subtask(subtask2)

        assert len(task._subtasks) == 2

        assert len(subtask1.children) == 1
        assert len(subtask1.parents) == 0
        assert subtask1.children[0] == subtask2

        assert len(subtask2.children) == 0
        assert len(subtask2.parents) == 1
        assert subtask2.parents[0] == subtask1

    def test_find_subtask(self):
        task = ToolkitTask("test", tool_names=["Calculator"])
        subtask1 = ToolSubtask("test1", tool_name="test", tool_action="test", tool_value="test")
        subtask2 = ToolSubtask("test2", tool_name="test", tool_action="test", tool_value="test")

        Pipeline().add_task(task)

        task.add_subtask(subtask1)
        task.add_subtask(subtask2)

        assert task.find_subtask(subtask1.id) == subtask1
        assert task.find_subtask(subtask2.id) == subtask2
    
    def test_find_tool(self):
        tool = MockTool()
        task = ToolkitTask("test", tool_names=[tool.name])

        Pipeline(
            tool_loader=ToolLoader(tools=[tool])
        ).add_task(task)

        assert task.find_tool(tool.name) == tool
