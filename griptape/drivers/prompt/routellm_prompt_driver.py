from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import Factory, define, field

from griptape.drivers import BasePromptDriver
from griptape.tokenizers.dummy_tokenizer import DummyTokenizer
from griptape.utils.import_utils import import_optional_dependency

if TYPE_CHECKING:
    from collections.abc import Iterator

    from routellm.controller import Controller

    from griptape.common import (
        DeltaMessage,
        Message,
        PromptStack,
    )
    from griptape.tokenizers import BaseTokenizer


@define
class RouteLlmPromptDriver(BasePromptDriver):
    """[RouteLlm](https://github.com/lm-sys/RouteLLM) Prompt Driver.

    Attributes:
        strong_prompt_driver: Prompt Driver to use when routing to the strong model.
        weak_prompt_driver: Prompt Driver to use when routing to the weak model.
        threshold: Cost threshold when routing between models.
        router: Router to use, defaults to "mf".
        client: RouteLlm Controller.
        tokenizer: Tokenizer to use, defaults to DummyTokenizer. After running, it will be set to the tokenizer of the routed prompt driver.
    """

    model: str = field(init=False, default=None)
    strong_prompt_driver: BasePromptDriver = field(
        kw_only=True,
        metadata={"serializable": False},
    )
    weak_prompt_driver: BasePromptDriver = field(
        kw_only=True,
        metadata={"serializable": False},
    )
    router: str = field(kw_only=True, default="mf", metadata={"serializable": True})
    threshold: float = field(kw_only=True, metadata={"serializable": True})
    client: Controller = field(
        kw_only=True,
        default=Factory(
            lambda self: import_optional_dependency("routellm.controller").Controller(
                routers=[self.router],
                strong_model=self.strong_prompt_driver.model,
                weak_model=self.weak_prompt_driver.model,
            ),
            takes_self=True,
        ),
        metadata={"serializable": False},
    )
    tokenizer: BaseTokenizer = field(
        init=False,
        default=Factory(
            lambda: DummyTokenizer(),
        ),
        kw_only=True,
    )

    def try_run(self, prompt_stack: PromptStack) -> Message:
        prompt_driver = self._get_prompt_driver(prompt_stack)

        return prompt_driver.try_run(prompt_stack)

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[DeltaMessage]:
        prompt_driver = self._get_prompt_driver(prompt_stack)

        return prompt_driver.try_stream(prompt_stack)

    def _get_prompt_driver(self, prompt_stack: PromptStack) -> BasePromptDriver:
        if prompt_stack.messages:
            prompt = prompt_stack.messages[-1].value
        else:
            raise ValueError("Prompt stack is empty.")

        if isinstance(prompt, str):
            routed_model = self.client.route(
                prompt=prompt,
                router=self.router,
                threshold=self.threshold,
            )
        else:
            raise ValueError("Prompt must be a string.")

        if routed_model == self.strong_prompt_driver.model:
            prompt_driver = self.strong_prompt_driver
        elif routed_model == self.weak_prompt_driver.model:
            prompt_driver = self.weak_prompt_driver
        else:
            raise ValueError(f"Model '{routed_model}' not found.")

        self.model = prompt_driver.model
        self.tokenizer = prompt_driver.tokenizer

        return prompt_driver
