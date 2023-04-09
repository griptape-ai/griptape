from attr import define
from skatepark.drivers import PromptDriver
from skatepark.utils import TiktokenTokenizer, Tokenizer
from skatepark.artifacts import TextOutput


@define
class MockValueDriver(PromptDriver):
    value: str
    model: str = "test-model"
    tokenizer: Tokenizer = TiktokenTokenizer()

    def try_run(self, **kwargs) -> TextOutput:
        return TextOutput(value=self.value, meta={})
