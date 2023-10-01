from attr import define
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import OpenAiTokenizer, BaseTokenizer
from griptape.artifacts import TextArtifact


@define
class MockValuePromptDriver(BasePromptDriver):
    value: str
    model: str = "test-model"
    tokenizer: BaseTokenizer = OpenAiTokenizer()

    def try_run(self, value: str) -> TextArtifact:
        return TextArtifact(value=self.value)
