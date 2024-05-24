from collections.abc import Iterator
from attr import define, field
from griptape.utils import PromptStack
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import BaseTokenizer
from griptape.artifacts import TextArtifact, TextChunkArtifact
from tests.mocks.mock_tokenizer import MockTokenizer


@define
class MockPromptDriver(BasePromptDriver):
    model: str = "test-model"
    tokenizer: BaseTokenizer = MockTokenizer(model="test-model", max_input_tokens=4096, max_output_tokens=4096)
    mock_output: str = field(default="mock output", kw_only=True)

    def try_run(self, prompt_stack: PromptStack) -> TextArtifact:
        return TextArtifact(value=self.mock_output)

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[TextChunkArtifact]:
        yield TextChunkArtifact(value=self.mock_output)
