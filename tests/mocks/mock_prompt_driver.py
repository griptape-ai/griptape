from attr import define
from griptape.utils import PromptStack
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import TiktokenTokenizer, BaseTokenizer
from griptape.artifacts import TextArtifact


@define
class MockPromptDriver(BasePromptDriver):
    model: str = "test-model"
    tokenizer: BaseTokenizer = TiktokenTokenizer()

    def try_run(self, prompt_stack: PromptStack) -> TextArtifact:
        return TextArtifact(value=f"mock output")
