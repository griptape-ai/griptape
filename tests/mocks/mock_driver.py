from attrs import define
from galaxybrain.drivers import PromptDriver
from galaxybrain.utils import TiktokenTokenizer, Tokenizer
from galaxybrain.workflows import StepOutput


@define()
class MockDriver(PromptDriver):
    tokenizer: Tokenizer = TiktokenTokenizer()

    def run(self, value: str) -> StepOutput:
        return StepOutput(value=f"mock output", meta={})
