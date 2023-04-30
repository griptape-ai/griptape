from attr import define
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import TiktokenTokenizer, BaseTokenizer
from griptape.artifacts import TextArtifact


@define
class MockValueDriver(BasePromptDriver):
    value: str
    model: str = "test-model"
    tokenizer: BaseTokenizer = TiktokenTokenizer()

    def try_run(self, **kwargs) -> TextArtifact:
        return TextArtifact(value=self.value)
