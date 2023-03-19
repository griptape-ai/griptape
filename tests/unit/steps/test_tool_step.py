from warpspeed.artifacts import ErrorOutput
from warpspeed.steps import ToolStep, ToolSubstep
from warpspeed.tools import PingPongTool
from tests.mocks.mock_value_driver import MockValueDriver
from warpspeed.structures import Pipeline


class TestToolStep:
    def test_run(self):
        output = """Output: done"""

        step = ToolStep("test", tool=PingPongTool(), max_substeps=10)
        pipeline = Pipeline(prompt_driver=MockValueDriver(output))

        pipeline.add_step(step)

        result = pipeline.run()

        assert len(step._substeps) == 1
        assert step._substeps[0].tool_input is None
        assert result.output.value == "done"

    def test_run_max_substeps(self):
        output = """Action: {"tool": "test"}"""

        step = ToolStep("test", tool=PingPongTool(), max_substeps=3)
        pipeline = Pipeline(prompt_driver=MockValueDriver(output))

        pipeline.add_step(step)

        pipeline.run()

        assert len(step._substeps) == 3
        assert isinstance(step.output, ErrorOutput)

    def test_init_from_prompt(self):
        valid_input = """Thought: need to test\nAction: {"tool": "test", "input": "test input"}\nObservation: test 
        observation\nOutput: test output"""
        step = ToolStep("test", tool=PingPongTool())

        Pipeline().add_step(step)

        substep = step.add_substep(ToolSubstep(valid_input))

        assert substep.thought == "need to test"
        assert substep.tool_name == "test"
        assert substep.tool_input == "test input"
        assert substep.output.value == "test output"

    def test_add_substep(self):
        step = ToolStep("test", tool=PingPongTool())
        substep1 = ToolSubstep("test1", tool_name="test", tool_input="test")
        substep2 = ToolSubstep("test2", tool_name="test", tool_input="test")

        Pipeline().add_step(step)

        step.add_substep(substep1)
        step.add_substep(substep2)

        assert len(step._substeps) == 2

        assert len(substep1.children) == 1
        assert len(substep1.parents) == 0
        assert substep1.children[0] == substep2

        assert len(substep2.children) == 0
        assert len(substep2.parents) == 1
        assert substep2.parents[0] == substep1

    def test_find_substep(self):
        step = ToolStep("test", tool=PingPongTool())
        substep1 = ToolSubstep("test1", tool_name="test", tool_input="test")
        substep2 = ToolSubstep("test2", tool_name="test", tool_input="test")

        Pipeline().add_step(step)

        step.add_substep(substep1)
        step.add_substep(substep2)

        assert step.find_substep(substep1.id) == substep1
        assert step.find_substep(substep2.id) == substep2

    def test_find_tool(self):
        tool = PingPongTool()
        step = ToolStep("test", tool=PingPongTool())

        assert step.find_tool(tool.name) == tool
