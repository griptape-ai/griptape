from galaxybrain.workflows import Workflow, ToolStep
from galaxybrain.tools import PingPongTool
from tests.mocks.mock_value_driver import MockValueDriver


class TestToolStep:
    def test_run(self):
        output = """Action: {"tool": "exit", "input": "test is finished"}"""

        step = ToolStep("test", tool=PingPongTool())
        workflow = Workflow(prompt_driver=MockValueDriver(output))

        workflow.add_step(step)

        result = workflow.start()

        assert len(step.substeps) == 1
        assert step.substeps[0].action_name == "exit"
        assert step.substeps[0].action_input == "test is finished"
        assert result.value == "test is finished"

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

