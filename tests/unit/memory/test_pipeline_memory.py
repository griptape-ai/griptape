from warpspeed.artifacts import TextOutput
from warpspeed.steps import PromptStep, ToolStep
from warpspeed.memory import PipelineMemory, PipelineRun
from warpspeed.structures import Pipeline
from warpspeed.tools import PingPongTool


class TestMemory:
    def test_is_empty(self):
        memory = PipelineMemory()

        assert memory.is_empty()

        memory.add_run(PipelineRun(prompt="test", output=TextOutput("test")))

        assert not memory.is_empty()

    def test_add_run(self):
        memory = PipelineMemory()
        run = PipelineRun(prompt="test", output=TextOutput("test"))

        memory.add_run(run)

        assert memory.runs[0] == run

    def test_to_string(self):
        memory = PipelineMemory()
        run = PipelineRun(prompt="test", output=TextOutput("test"))

        memory.add_run(run)

        assert "Input: test\nOutput: test" in memory.to_prompt_string()