from attrs import define
from warpspeed.drivers import PromptDriver
from warpspeed.utils import TiktokenTokenizer, Tokenizer
from warpspeed.artifacts import TextOutput


@define()
class MockValueDriver(PromptDriver):
    value: str
    tokenizer: Tokenizer = TiktokenTokenizer()

    def run(self, **kwargs) -> TextOutput:
        return TextOutput(value=self.value, meta={})
