from attr import define
from skatepark.drivers import PromptDriver
from skatepark.utils import TiktokenTokenizer, Tokenizer
from skatepark.artifacts import TextOutput


@define
class MockDriver(PromptDriver):
    model: str = "test-model"
    tokenizer: Tokenizer = TiktokenTokenizer()

    def try_run(self, value: str) -> TextOutput:
        return TextOutput(value=f"mock output", meta={})
