from __future__ import annotations

from attr import define, field

from griptape.defaults import BaseStructureDefaultsProvider
from griptape.drivers import BaseEmbeddingDriver, BasePromptDriver, OpenAiChatPromptDriver, OpenAiEmbeddingDriver
from griptape.memory import TaskMemory
from griptape.tokenizers import OpenAiTokenizer


@define
class OpenAiStructureDefaultsProvider(BaseStructureDefaultsProvider):
    prompt_driver: BasePromptDriver = field(
        default=OpenAiChatPromptDriver(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_4_MODEL)
    )
    embedding_driver: BaseEmbeddingDriver = field(default=OpenAiEmbeddingDriver(), kw_only=True)
    task_memory: TaskMemory = field(default=TaskMemory(), kw_only=True)
