from attrs import define
from warpspeed.drivers import PromptDriver
from warpspeed.utils import TiktokenTokenizer, Tokenizer
from warpspeed.artifacts import TextOutput


@define
class MockDriver(PromptDriver):
    model: str = "test-model"
    tokenizer: Tokenizer = TiktokenTokenizer()

    def try_run(self, value: str) -> TextOutput:
        return TextOutput(value=f"mock output", meta={})
