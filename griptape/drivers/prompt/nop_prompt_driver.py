from griptape.drivers import BaseEmbeddingDriver
from griptape.exceptions import NopException
from griptape.utils.prompt_stack import PromptStack


class NopPromptDriver(BaseEmbeddingDriver):
    def try_run(self, prompt_stack: PromptStack) -> list[float]:
        raise NopException(__class__.__name__, "try_run")

    def try_stream(self, prompt_stack: PromptStack) -> list[float]:
        raise NopException(__class__.__name__, "try_stream")
