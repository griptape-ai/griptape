from warpspeed.steps import ToolStep, ToolSubstep
from warpspeed.tools import PingPongTool
from tests.mocks.mock_value_driver import MockValueDriver
from warpspeed.structures import Pipeline


class TestToolStep:
    def test_run(self):
        output = """Action: {"tool": "exit", "input": "test is finished"}"""

        step = ToolStep("test", tool=PingPongTool())
        pipeline = Pipeline(prompt_driver=MockValueDriver(output))

        pipeline.add_step(step)

        result = pipeline.run()

        assert len(step.substeps) == 1
        assert step.substeps[0].action_name == "exit"
        assert step.substeps[0].action_input == "test is finished"
        assert result.output.value == "test is finished"

    def test_parse_tool_action(self):
        valid_json = """{"tool": "test", "input": "test input"}"""
        invalid_json = """{"tool"$ "test", "input"^ "test input"}"""
        success_result = ("test", "test input")
        error_result = ("error", ToolStep.JSON_PARSE_ERROR_MSG)
        step = ToolStep("test", tool=PingPongTool())

        assert step.parse_tool_action("") == error_result
        assert step.parse_tool_action(valid_json) == error_result
        assert step.parse_tool_action(f"Something Action: {valid_json}") == error_result
        assert step.parse_tool_action(f"Something\nAction: {valid_json} something") == error_result
        assert step.parse_tool_action(f"Action: {invalid_json}") == error_result

        assert step.parse_tool_action(f"Action: {valid_json}") == success_result
        assert step.parse_tool_action(f"Action:{valid_json}") == success_result
        assert step.parse_tool_action(f"Something\nAction: {valid_json}") == success_result
        assert step.parse_tool_action(f"Something\nAction: {valid_json}\n") == success_result
        assert step.parse_tool_action(f"Something\nAction: {valid_json}\n\n") == success_result

    def test_add_substep(self):
        step = ToolStep("test", tool=PingPongTool())
        substep1 = ToolSubstep("test1", tool_step=step, action_name="exit", action_input="test")
        substep2 = ToolSubstep("test2", tool_step=step, action_name="exit", action_input="test")

        step.add_substep(substep1)
        step.add_substep(substep2)

        assert len(step.substeps) == 2

        assert len(substep1.children) == 1
        assert len(substep1.parents) == 0
        assert substep1.children[0] == substep2

        assert len(substep2.children) == 0
        assert len(substep2.parents) == 1
        assert substep2.parents[0] == substep1

    def test_find_substep(self):
        step = ToolStep("test", tool=PingPongTool())
        substep1 = ToolSubstep("test1", tool_step=step, action_name="exit", action_input="test")
        substep2 = ToolSubstep("test2", tool_step=step, action_name="exit", action_input="test")

        step.add_substep(substep1)
        step.add_substep(substep2)

        assert step.find_substep(substep1.id) == substep1
        assert step.find_substep(substep2.id) == substep2

    def test_find_tool(self):
        tool = PingPongTool()
        step = ToolStep("test", tool=PingPongTool())

        assert step.find_tool(tool.name) == tool