from warpspeed.steps import PromptStep, ToolStep
from warpspeed.memory import Memory
from warpspeed.tools import PingPongTool


class TestMemory:
    def test_is_empty(self):
        memory = Memory()

        assert memory.is_empty()

        memory.before_run(PromptStep("test"))

        assert not memory.is_empty()

    def test_before_run(self):
        memory = Memory()
        step = PromptStep("test")

        memory.before_run(step)

        assert memory.steps[0] == step

    def test_to_string_with_prompt_step(self):
        memory = Memory()
        step = PromptStep("test")

        memory.before_run(step)

        assert "Q: test" in memory.to_prompt_string()

    def test_to_string_with_tool_step(self):
        memory = Memory()
        step = ToolStep("test", tool=PingPongTool())

        memory.before_run(step)

        assert "Q: test" in memory.to_prompt_string()
