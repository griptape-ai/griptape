from tests.mocks.mock_tool.tool import MockTool
from griptape.artifacts import ErrorOutput
from griptape.tasks import ToolkitTask, ToolStep
from griptape.utils import ToolLoader
from tests.mocks.mock_value_driver import MockValueDriver
from griptape.structures import Pipeline


class TestToolkitStep:
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
        assert len(task._steps) == 1
        assert result.output.value == "done"
    
    def test_run_max_steps(self):
        output = """Action: {"tool": "test"}"""

        task = ToolkitTask("test", tool_names=["Calculator"], max_steps=3)
        pipeline = Pipeline(prompt_driver=MockValueDriver(output))

        pipeline.add_task(task)

        pipeline.run()

        assert len(task._steps) == 3
        assert isinstance(task.output, ErrorOutput)

    def test_init_from_prompt_1(self):
        valid_input = """Thought: need to test\nAction: {"tool": "test", "action": "test action", "value": "test input"}\nObservation: test 
        observation\nOutput: test output"""
        task = ToolkitTask("test", tool_names=["Calculator"])

        Pipeline().add_task(task)

        step = task.add_step(ToolStep(valid_input))

        assert step.thought == "need to test"
        assert step.tool_name == "test"
        assert step.tool_action == "test action"
        assert step.tool_value == "test input"
        assert step.output is None

    def test_init_from_prompt_2(self):
        valid_input = """Thought: need to test\nObservation: test 
        observation\nOutput: test output"""
        task = ToolkitTask("test", tool_names=["Calculator"])

        Pipeline().add_task(task)

        step = task.add_step(ToolStep(valid_input))

        assert step.thought == "need to test"
        assert step.tool_name is None
        assert step.tool_action is None
        assert step.tool_value is None
        assert step.output.value == "test output"

    def test_add_step(self):
        task = ToolkitTask("test", tool_names=["Calculator"])
        step1 = ToolStep("test1", tool_name="test", tool_action="test", tool_value="test")
        step2 = ToolStep("test2", tool_name="test", tool_action="test", tool_value="test")

        Pipeline().add_task(task)

        task.add_step(step1)
        task.add_step(step2)

        assert len(task._steps) == 2

        assert len(step1.children) == 1
        assert len(step1.parents) == 0
        assert step1.children[0] == step2

        assert len(step2.children) == 0
        assert len(step2.parents) == 1
        assert step2.parents[0] == step1

    def test_find_step(self):
        task = ToolkitTask("test", tool_names=["Calculator"])
        step1 = ToolStep("test1", tool_name="test", tool_action="test", tool_value="test")
        step2 = ToolStep("test2", tool_name="test", tool_action="test", tool_value="test")

        Pipeline().add_task(task)

        task.add_step(step1)
        task.add_step(step2)

        assert task.find_step(step1.id) == step1
        assert task.find_step(step2.id) == step2
    
    def test_find_tool(self):
        tool = MockTool()
        task = ToolkitTask("test", tool_names=[tool.name])

        Pipeline(
            tool_loader=ToolLoader(tools=[tool])
        ).add_task(task)

        assert task.find_tool(tool.name) == tool
