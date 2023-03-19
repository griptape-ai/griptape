from warpspeed.steps import PromptStep
from tests.mocks.mock_driver import MockDriver
from warpspeed.structures import Pipeline


class TestPromptStep:
    def test_run(self):
        step = PromptStep("test")
        pipeline = Pipeline(prompt_driver=MockDriver())

        pipeline.add_step(step)

        assert step.run().value == "mock output"

    def test_render_prompt(self):
        step = PromptStep("{{ test }}", context={"test": "test value"})

        Pipeline().add_step(step)

        assert step.render_prompt() == "test value"

    def test_full_context(self):
        parent = PromptStep("parent")
        step = PromptStep("test", context={"foo": "bar"})
        child = PromptStep("child")
        pipeline = Pipeline(prompt_driver=MockDriver())

        pipeline.add_steps(parent, step, child)

        pipeline.run()

        context = step.full_context

        assert context["foo"] == "bar"
        assert context["input"] == parent.output.value
        assert context["structure"] == pipeline
        assert context["parent"] == parent
        assert context["child"] == child
