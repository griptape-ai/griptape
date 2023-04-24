from attr import define
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import TiktokenTokenizer, BaseTokenizer
from griptape.artifacts import TextOutput


@define
class MockDriver(BasePromptDriver):
    model: str = "test-model"
    tokenizer: BaseTokenizer = TiktokenTokenizer()

    def try_run(self, value: str) -> TextOutput:
        return TextOutput(value=f"mock output", meta={})
