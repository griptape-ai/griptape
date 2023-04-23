from griptape.tools import Calculator, WebSearch
from griptape.artifacts import ErrorOutput
from griptape.steps import ToolkitStep, ToolSubstep
from griptape.utils import ToolLoader
from tests.mocks.mock_value_driver import MockValueDriver
from griptape.structures import Pipeline


class TestToolkitStep:
    def test_init(self):
        assert len(ToolkitStep("test", tool_names=["Calculator", "WebSearch"]).tool_names) == 2

        try:
            assert ToolkitStep("test", tool_names=["Calculator", "Calculator"])
        except ValueError:
            assert True

    def test_run(self):
        output = """Output: done"""

        tools = [
            Calculator(),
            WebSearch()
        ]

        step = ToolkitStep("test", tool_names=["Calculator", "WebSearch"])
        pipeline = Pipeline(
            prompt_driver=MockValueDriver(output),
            tool_loader=ToolLoader(tools=tools)
        )

        pipeline.add_step(step)

        result = pipeline.run()

        assert len(step.tools) == 2
        assert len(step._substeps) == 1
        assert result.output.value == "done"
    
    def test_run_max_substeps(self):
        output = """Action: {"tool": "test"}"""

        step = ToolkitStep("test", tool_names=["Calculator"], max_substeps=3)
        pipeline = Pipeline(prompt_driver=MockValueDriver(output))

        pipeline.add_step(step)

        pipeline.run()

        assert len(step._substeps) == 3
        assert isinstance(step.output, ErrorOutput)

    def test_init_from_prompt_1(self):
        valid_input = """Thought: need to test\nAction: {"tool": "test", "action": "test action", "value": "test input"}\nObservation: test 
        observation\nOutput: test output"""
        step = ToolkitStep("test", tool_names=["Calculator"])

        Pipeline().add_step(step)

        substep = step.add_substep(ToolSubstep(valid_input))

        assert substep.thought == "need to test"
        assert substep.tool_name == "test"
        assert substep.tool_action == "test action"
        assert substep.tool_value == "test input"
        assert substep.output is None

    def test_init_from_prompt_2(self):
        valid_input = """Thought: need to test\nObservation: test 
        observation\nOutput: test output"""
        step = ToolkitStep("test", tool_names=["Calculator"])

        Pipeline().add_step(step)

        substep = step.add_substep(ToolSubstep(valid_input))

        assert substep.thought == "need to test"
        assert substep.tool_name is None
        assert substep.tool_action is None
        assert substep.tool_value is None
        assert substep.output.value == "test output"

    def test_add_substep(self):
        step = ToolkitStep("test", tool_names=["Calculator"])
        substep1 = ToolSubstep("test1", tool_name="test", tool_action="test", tool_value="test")
        substep2 = ToolSubstep("test2", tool_name="test", tool_action="test", tool_value="test")

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
        step = ToolkitStep("test", tool_names=["Calculator"])
        substep1 = ToolSubstep("test1", tool_name="test", tool_action="test", tool_value="test")
        substep2 = ToolSubstep("test2", tool_name="test", tool_action="test", tool_value="test")

        Pipeline().add_step(step)

        step.add_substep(substep1)
        step.add_substep(substep2)

        assert step.find_substep(substep1.id) == substep1
        assert step.find_substep(substep2.id) == substep2
    
    def test_find_tool(self):
        tool = Calculator()
        step = ToolkitStep("test", tool_names=[tool.name])

        Pipeline(
            tool_loader=ToolLoader(tools=[tool])
        ).add_step(step)

        assert step.find_tool(tool.name) == tool
