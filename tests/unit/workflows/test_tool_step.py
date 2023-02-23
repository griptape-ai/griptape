from galaxybrain.prompts import Prompt
from galaxybrain.workflows import Workflow, ToolStep
from tests.mocks.mock_value_driver import MockValueDriver


class TestToolStep:
    def test_run(self):
        step = ToolStep(input=Prompt("test"))
        workflow = Workflow(completion_driver=MockValueDriver())

        workflow.add_step(step)

        assert step.run().value == "Conversation begins:\n\n"
