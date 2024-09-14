from __future__ import annotations

import uuid
from abc import ABC
from typing import TYPE_CHECKING, Any, Optional

from attrs import Factory, define, field

from griptape.common import Message, PromptStack
from griptape.mixins.futures_executor_mixin import FuturesExecutorMixin

if TYPE_CHECKING:
    from griptape.engines.rag import RagContext


@define(kw_only=True)
class BaseRagModule(FuturesExecutorMixin, ABC):
    name: str = field(
        default=Factory(lambda self: f"{self.__class__.__name__}-{uuid.uuid4().hex}", takes_self=True), kw_only=True
    )

    def generate_prompt_stack(self, system_prompt: Optional[str], query: str) -> PromptStack:
        messages = []

        if system_prompt is not None:
            messages.append(Message(system_prompt, role=Message.SYSTEM_ROLE))

        messages.append(Message(query, role=Message.USER_ROLE))

        return PromptStack(messages=messages)

    def get_context_param(self, context: RagContext, key: str) -> Optional[Any]:
        return context.module_configs.get(self.name, {}).get(key)

    def set_context_param(self, context: RagContext, key: str, value: Any) -> None:
        if not isinstance(context.module_configs.get(self.name), dict):
            context.module_configs[self.name] = {}

        context.module_configs[self.name][key] = value
