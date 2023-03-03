from galaxybrain.workflows import Workflow, PromptStep
from tests.mocks.mock_driver import MockDriver


class TestPromptStep:
    def test_run(self):
        step = PromptStep("test")
        workflow = Workflow(prompt_driver=MockDriver())

        workflow.add_step(step)

        assert step.run().value == "mock output"

    def test_render_prompt(self):
        assert PromptStep("{{ test }}", context={"test": "test value"}).render_prompt() == "test value"

    def test_default_context(self):
        parent = PromptStep("parent")
        step = PromptStep("test")
        child = PromptStep("child")
        workflow = Workflow(prompt_driver=MockDriver())

        workflow.add_steps(parent, step, child)

        workflow.start()

        context = step.default_context

        assert context["workflow"] == workflow
        assert context["input"] == parent.output
        assert context["parent"] == parent
        assert context["child"] == child
