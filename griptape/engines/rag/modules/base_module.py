from abc import ABC
from concurrent import futures
from attr import define, field, Factory

from griptape.utils import PromptStack


@define(kw_only=True)
class BaseModule(ABC):
    futures_executor: futures.Executor = field(default=Factory(lambda: futures.ThreadPoolExecutor()))

    def generate_query_prompt_stack(self, system_prompt: str, query: str) -> PromptStack:
        return PromptStack(
            inputs=[
                PromptStack.Input(system_prompt, role=PromptStack.SYSTEM_ROLE),
                PromptStack.Input(query, role=PromptStack.USER_ROLE),
            ]
        )
