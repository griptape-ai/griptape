from attr import define, field
from griptape.events import CompletionChunkEvent
from griptape.utils import PromptStack
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import OpenAiTokenizer, BaseTokenizer
from griptape.artifacts import TextArtifact


@define
class MockPromptDriver(BasePromptDriver):
    model: str = "test-model"
    tokenizer: BaseTokenizer = OpenAiTokenizer(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL)
    mock_output: str = field(default="mock output", kw_only=True)

    def try_run(self, prompt_stack: PromptStack) -> TextArtifact:
        if self.structure:
            self.structure.publish_event(CompletionChunkEvent(token=self.mock_output))
        return TextArtifact(value=self.mock_output)
