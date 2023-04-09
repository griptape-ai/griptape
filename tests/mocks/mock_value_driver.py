from attr import define
from warpspeed.drivers import PromptDriver
from warpspeed.utils import TiktokenTokenizer, Tokenizer
from warpspeed.artifacts import TextOutput


@define
class MockValueDriver(PromptDriver):
    value: str
    model: str = "test-model"
    tokenizer: Tokenizer = TiktokenTokenizer()

    def try_run(self, **kwargs) -> TextOutput:
        return TextOutput(value=self.value, meta={})
