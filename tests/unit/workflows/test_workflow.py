from galaxybrain.rules import Rule
from galaxybrain.utils import TiktokenTokenizer
from galaxybrain.workflows import Workflow, PromptStep, StepInput, StepOutput
from tests.mocks.mock_driver import MockDriver


class TestWorkflow:
    def test_constructor(self):
        rule = Rule("test")
        driver = MockDriver()
        workflow = Workflow(prompt_driver=driver, rules=[rule])

        assert workflow.prompt_driver is driver
        assert workflow.root_step is None
        assert workflow.rules[0].value is "test"
        assert workflow.memory is not None

    def test_steps_order(self):
        first_step = PromptStep("test1")
        second_step = PromptStep("test2")
        third_step = PromptStep("test3")

        workflow = Workflow(
            prompt_driver=MockDriver(),
            root_step=first_step
        )

        workflow.add_step(second_step)
        workflow.add_step(third_step)

        assert workflow.steps()[0] is first_step
        assert workflow.steps()[1] is second_step
        assert workflow.steps()[2] is third_step
        assert workflow.last_step() is third_step

    def test_add_step(self):
        step = PromptStep("test")
        workflow = Workflow(prompt_driver=MockDriver())

        workflow.add_step(step)

        assert step in workflow.steps()

    def test_add_steps(self):
        step1 = PromptStep("test1")
        step2 = PromptStep("test2")
        workflow = Workflow(prompt_driver=MockDriver())

        workflow.add_steps(step1, step2)

        assert step1 in workflow.steps()
        assert step2 in workflow.steps()

    def test_to_prompt_string(self):
        workflow = Workflow(
            prompt_driver=MockDriver(),
            root_step=PromptStep("test")
        )

        workflow.start()

        assert "mock output" in workflow.to_prompt_string()

    def test_token_count(self):
        workflow = Workflow(prompt_driver=MockDriver())

        assert workflow.token_count() == TiktokenTokenizer().token_count(workflow.to_prompt_string())

    def test_step_input_token_count(self):
        text = "foobar"

        assert StepInput(text).token_count() == TiktokenTokenizer().token_count(text)

    def test_step_output_token_count(self):
        text = "foobar"

        assert StepOutput(text).token_count() == TiktokenTokenizer().token_count(text)

    def test_start(self):
        workflow = Workflow(prompt_driver=MockDriver())
        workflow.add_step(PromptStep("test"))

        assert "mock output" in workflow.start().value

    def test_resume(self):
        workflow = Workflow(prompt_driver=MockDriver())
        workflow.add_step(PromptStep("test"))

        assert "mock output" in workflow.resume().value
