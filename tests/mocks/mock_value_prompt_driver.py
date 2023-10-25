from typing import Iterator
from attr import define
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import OpenAiTokenizer, BaseTokenizer
from griptape.artifacts import TextArtifact


@define
class MockValuePromptDriver(BasePromptDriver):
    value: str
    model: str = "test-model"
    tokenizer: BaseTokenizer = OpenAiTokenizer(
        model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL
    )

    def try_run(self, value: str) -> TextArtifact:
        return TextArtifact(value=self.value)

    def try_stream(self, value: str) -> Iterator[TextArtifact]:
        yield TextArtifact(value=self.value)
