from attrs import define
from warpspeed.drivers import PromptDriver
from warpspeed.utils import TiktokenTokenizer, Tokenizer
from warpspeed.artifacts import TextOutput


@define()
class MockDriver(PromptDriver):
    tokenizer: Tokenizer = TiktokenTokenizer()

    def run(self, value: str) -> TextOutput:
        return TextOutput(value=f"mock output", meta={})
