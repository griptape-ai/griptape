from attrs import define
from galaxybrain.drivers import PromptDriver
from galaxybrain.utils import TiktokenTokenizer, Tokenizer
from galaxybrain.artifacts import TextOutput


@define()
class MockDriver(PromptDriver):
    tokenizer: Tokenizer = TiktokenTokenizer()

    def run(self, value: str) -> TextOutput:
        return TextOutput(value=f"mock output", meta={})
