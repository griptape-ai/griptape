from jinja2 import Environment
from galaxybrain.prompts import Prompt
from galaxybrain.rules import Rule
from galaxybrain.workflows import Workflow, CompletionStep, StepOutput, Memory
from tests.mocks.mock_driver import MockCompletionDriver


class TestPrompt:
    def test_j2(self):
        assert isinstance(Prompt.j2(), Environment)

    def test_summarize(self):
        step = CompletionStep(input=Prompt("hello"))
        step.output = StepOutput("goodbye")

        assert Prompt.summarize("test summary", [step], "../tests/templates") == "test summary\nhello\ngoodbye\n"

    def test_intro(self):
        assert Prompt.intro([Rule("be good")], "../tests/templates") == "be good\n"

    def test_conversation(self):
        step = CompletionStep(input=Prompt("hello"))
        step.output = StepOutput("goodbye")
        memory = Memory(steps=[(step, False)], summary="test summary")
        workflow = Workflow(memory=memory, completion_driver=MockCompletionDriver())
        prompt = Prompt.conversation(workflow, "../tests/templates")

        assert prompt == "test summary\nhello\ngoodbye\n"
