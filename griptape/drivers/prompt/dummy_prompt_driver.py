from collections.abc import Iterator
from attrs import field, Factory, define
from griptape.tokenizers import DummyTokenizer
from griptape.drivers import BasePromptDriver
from griptape.artifacts import TextArtifact, TextChunkArtifact
from griptape.exceptions import DummyException
from griptape.utils.prompt_stack import PromptStack


@define
class DummyPromptDriver(BasePromptDriver):
    model: None = field(init=False, default=None, kw_only=True)
    tokenizer: DummyTokenizer = field(default=Factory(lambda: DummyTokenizer()), kw_only=True)

    def try_run(self, prompt_stack: PromptStack) -> TextArtifact:
        raise DummyException(__class__.__name__, "try_run")

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[TextChunkArtifact]:
        raise DummyException(__class__.__name__, "try_stream")
