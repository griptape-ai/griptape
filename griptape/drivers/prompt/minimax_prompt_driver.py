from __future__ import annotations

from attrs import Factory, define, field

from griptape.drivers.prompt.openai import OpenAiChatPromptDriver
from griptape.tokenizers.minimax_tokenizer import MinimaxTokenizer


@define
class MinimaxPromptDriver(OpenAiChatPromptDriver):
    model: str = field(default="MiniMax-M3.1-Flash", kw_only=True, metadata={"serializable": True})
    base_url: str = field(default="https://api.minimax.io/v1", kw_only=True, metadata={"serializable": True})
    tokenizer: MinimaxTokenizer = field(
        default=Factory(lambda self: MinimaxTokenizer(model=self.model), takes_self=True),
        kw_only=True,
        metadata={"serializable": True},
    )
