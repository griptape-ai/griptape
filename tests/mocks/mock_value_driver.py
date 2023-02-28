from attrs import define
from galaxybrain.drivers import PromptDriver
from galaxybrain.utils import TiktokenTokenizer, Tokenizer
from galaxybrain.workflows import StepOutput


@define()
class MockValueDriver(PromptDriver):
    value: str
    tokenizer: Tokenizer = TiktokenTokenizer()

    def run(self, **kwargs) -> StepOutput:
        return StepOutput(value=self.value, meta={})
