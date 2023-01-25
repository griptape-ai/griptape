from galaxybrain.prompts import Prompt
from galaxybrain.workflows import CompletionStep
from galaxybrain.workflows.memory import Memory


class TestMemory:
    def test_is_empty(self):
        memory = Memory()

        assert memory.is_empty()

        memory.before_run(CompletionStep(input=Prompt("test")))

        assert not memory.is_empty()

    def test_before_run(self):
        memory = Memory()
        step = CompletionStep(input=Prompt("test"))

        memory.before_run(step)

        assert memory.steps[0] == step

    def test_to_string(self):
        memory = Memory()
        step = CompletionStep(input=Prompt("test"))

        memory.before_run(step)

        assert "Q: test" in memory.to_prompt_string()
