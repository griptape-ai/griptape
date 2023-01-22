from attrs import define
from galaxybrain.drivers import Driver
from galaxybrain.workflows import StepOutput


@define()
class MockDriver(Driver):
    def run(self, value: str) -> StepOutput:
        return StepOutput(value=f"ack {value}", meta={})
