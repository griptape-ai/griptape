from collections.abc import Iterator
from attrs import field, Factory, define
from griptape.tokenizers import NopTokenizer
from griptape.drivers import BasePromptDriver
from griptape.artifacts import TextArtifact
from griptape.exceptions import NopException
from griptape.utils.prompt_stack import PromptStack


@define
class NopPromptDriver(BasePromptDriver):
    model: str = field(init=False)
    tokenizer: NopTokenizer = field(default=Factory(lambda: NopTokenizer()), kw_only=True)

    def try_run(self, prompt_stack: PromptStack) -> TextArtifact:
        raise NopException(__class__.__name__, "try_run")

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[TextArtifact]:
        raise NopException(__class__.__name__, "try_stream")
