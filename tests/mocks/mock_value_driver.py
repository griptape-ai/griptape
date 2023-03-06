from attrs import define
from galaxybrain.drivers import PromptDriver
from galaxybrain.utils import TiktokenTokenizer, Tokenizer
from galaxybrain.artifacts import TextOutput


@define()
class MockValueDriver(PromptDriver):
    value: str
    tokenizer: Tokenizer = TiktokenTokenizer()

    def run(self, **kwargs) -> TextOutput:
        return TextOutput(value=self.value, meta={})
