import json
from warpspeed.artifacts import TextOutput
from warpspeed.rules import Rule
from warpspeed.utils import TiktokenTokenizer
from warpspeed.steps import PromptStep, Step
from warpspeed.memory import PipelineMemory
from tests.mocks.mock_driver import MockDriver
from warpspeed.structures import Pipeline


class TestPipeline:
    def test_constructor(self):
        rule = Rule("test")
        driver = MockDriver()
        pipeline = Pipeline(prompt_driver=driver, rules=[rule])

        assert pipeline.prompt_driver is driver
        assert pipeline.first_step() is None
        assert pipeline.last_step() is None
        assert pipeline.rules[0].value is "test"
        assert pipeline.memory is None

    def test_with_memory(self):
        first_step = PromptStep("test1")
        second_step = PromptStep("test2")
        third_step = PromptStep("test3")

        pipeline = Pipeline(
            prompt_driver=MockDriver(),
            memory=PipelineMemory()
        )

        pipeline.add_steps(first_step, second_step, third_step)

        assert pipeline.memory is not None
        assert len(pipeline.memory.runs) == 0

        pipeline.run()
        pipeline.run()
        pipeline.run()

        assert len(pipeline.memory.runs) == 3

    def test_steps_order(self):
        first_step = PromptStep("test1")
        second_step = PromptStep("test2")
        third_step = PromptStep("test3")

        pipeline = Pipeline(
            prompt_driver=MockDriver()
        )

        pipeline.add_step(first_step)
        pipeline.add_step(second_step)
        pipeline.add_step(third_step)

        assert pipeline.first_step().id is first_step.id
        assert pipeline.steps[1].id is second_step.id
        assert pipeline.steps[2].id is third_step.id
        assert pipeline.last_step().id is third_step.id

    def test_add_step(self):
        first_step = PromptStep("test1")
        second_step = PromptStep("test2")

        pipeline = Pipeline(
            prompt_driver=MockDriver()
        )

        pipeline.add_step(first_step)
        pipeline.add_step(second_step)

        assert len(pipeline.steps) == 2
        assert first_step in pipeline.steps
        assert second_step in pipeline.steps
        assert first_step.structure == pipeline
        assert second_step.structure == pipeline
        assert len(first_step.parents) == 0
        assert len(first_step.children) == 1
        assert len(second_step.parents) == 1
        assert len(second_step.children) == 0

    def test_add_steps(self):
        first_step = PromptStep("test1")
        second_step = PromptStep("test2")

        pipeline = Pipeline(
            prompt_driver=MockDriver()
        )

        pipeline.add_steps(first_step, second_step)

        assert len(pipeline.steps) == 2
        assert first_step in pipeline.steps
        assert second_step in pipeline.steps
        assert first_step.structure == pipeline
        assert second_step.structure == pipeline
        assert len(first_step.parents) == 0
        assert len(first_step.children) == 1
        assert len(second_step.parents) == 1
        assert len(second_step.children) == 0

    def test_to_prompt_string(self):
        pipeline = Pipeline(
            prompt_driver=MockDriver(),
        )

        step = PromptStep("test")

        pipeline.add_step(step)

        pipeline.run()

        assert "mock output" in pipeline.to_prompt_string(step)

    def test_step_output_token_count(self):
        text = "foobar"

        assert TextOutput(text).token_count() == TiktokenTokenizer().token_count(text)

    def test_run(self):
        step = PromptStep("test")
        pipeline = Pipeline(prompt_driver=MockDriver())
        pipeline.add_step(step)

        assert step.state == Step.State.PENDING

        result = pipeline.run()

        assert "mock output" in result.output.value
        assert step.state == Step.State.FINISHED

    def test_run_with_args(self):
        step = PromptStep("{{ args[0] }}-{{ args[1] }}")
        pipeline = Pipeline(prompt_driver=MockDriver())
        pipeline.add_steps(step)

        pipeline._execution_args = ("test1", "test2")

        assert step.render_prompt() == "test1-test2"

        pipeline.run()

        assert step.render_prompt() == "-"

    def test_to_json(self):
        pipeline = Pipeline()

        pipeline.add_steps(
            PromptStep("test prompt"),
            PromptStep("test prompt")
        )

        assert len(json.loads(pipeline.to_json())["steps"]) == 2

    def test_to_dict(self):
        pipeline = Pipeline()

        pipeline.add_steps(
            PromptStep("test prompt"),
            PromptStep("test prompt")
        )

        assert len(pipeline.to_dict()["steps"]) == 2

    def test_from_json(self):
        pipeline = Pipeline()

        pipeline.add_steps(
            PromptStep("test prompt"),
            PromptStep("test prompt")
        )

        workflow_json = pipeline.to_json()

        assert len(Pipeline.from_json(workflow_json).steps) == 2

    def test_from_dict(self):
        pipeline = Pipeline()

        pipeline.add_steps(
            PromptStep("test prompt"),
            PromptStep("test prompt")
        )

        workflow_json = pipeline.to_dict()

        assert len(Pipeline.from_dict(workflow_json).steps) == 2

    def test_context(self):
        parent = PromptStep("parent")
        step = PromptStep("test")
        child = PromptStep("child")
        pipeline = Pipeline(prompt_driver=MockDriver())

        pipeline.add_steps(parent, step, child)

        context = pipeline.context(step)

        assert context["input"] is None

        pipeline.run()

        context = pipeline.context(step)

        assert context["input"] == parent.output.value
        assert context["structure"] == pipeline
        assert context["parent"] == parent
        assert context["child"] == child
