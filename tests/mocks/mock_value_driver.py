from attrs import define
from galaxybrain.drivers import CompletionDriver
from galaxybrain.workflows import StepOutput


@define()
class MockValueDriver(CompletionDriver):
    def run(self, value: str) -> StepOutput:
        return StepOutput(value=value, meta={})
