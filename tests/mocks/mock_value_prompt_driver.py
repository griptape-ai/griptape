from collections.abc import Iterator
from attr import define, field, Factory
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import OpenAiTokenizer, BaseTokenizer
from griptape.artifacts import TextArtifact
from griptape.utils.prompt_stack import PromptStack


@define
class MockValuePromptDriver(BasePromptDriver):
    value: str = field(kw_only=True)
    model: str = field(default="test-model")
    tokenizer: BaseTokenizer = field(
        default=Factory(lambda: OpenAiTokenizer(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL))
    )

    def try_run(self, prompt_stack: PromptStack) -> TextArtifact:
        return TextArtifact(value=self.value)

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[TextArtifact]:
        yield TextArtifact(value=self.value)
