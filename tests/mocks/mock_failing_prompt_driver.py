from attr import define
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import TiktokenTokenizer, BaseTokenizer
from griptape.artifacts import TextArtifact


@define
class MockFailingPromptDriver(BasePromptDriver):
    max_failures: int
    current_attempt: int = 0
    model: str = "test-model"
    tokenizer: BaseTokenizer = TiktokenTokenizer()

    def try_run(self, **kwargs) -> TextArtifact:
        if self.current_attempt < self.max_failures:
            self.current_attempt += 1

            raise Exception(f"failed attempt")
        else:
            return TextArtifact("success")
