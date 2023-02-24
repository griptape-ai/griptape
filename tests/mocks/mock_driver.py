from attrs import define
from galaxybrain.drivers import CompletionDriver
from galaxybrain.utils import TiktokenTokenizer, Tokenizer
from galaxybrain.workflows import StepOutput


@define()
class MockDriver(CompletionDriver):
    tokenizer: Tokenizer = TiktokenTokenizer()

    def run(self, value: str) -> StepOutput:
        return StepOutput(value=f"mock output", meta={})
