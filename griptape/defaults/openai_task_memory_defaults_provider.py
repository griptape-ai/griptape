from __future__ import annotations
from attr import define, field

from griptape.defaults import BaseDefaultsProvider
from griptape.drivers import BaseEmbeddingDriver, BasePromptDriver, OpenAiChatPromptDriver, OpenAiEmbeddingDriver
from griptape.tokenizers import OpenAiTokenizer


@define
class OpenAiTaskMemoryDefaultsProvider(BaseDefaultsProvider):
    query_engine_prompt_driver: BasePromptDriver = field(
        default=OpenAiChatPromptDriver(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_4_MODEL)
    )
    query_engine_embedding_driver: BaseEmbeddingDriver = field(default=OpenAiEmbeddingDriver())
    summary_engine_prompt_driver: BasePromptDriver = field(
        default=OpenAiChatPromptDriver(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_4_MODEL)
    )
    csv_extraction_engine_prompt_driver: BasePromptDriver = field(
        default=OpenAiChatPromptDriver(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_4_MODEL)
    )
    json_extraction_engine_prompt_driver: BasePromptDriver = field(
        default=OpenAiChatPromptDriver(model=OpenAiTokenizer.DEFAULT_OPENAI_GPT_4_MODEL)
    )
