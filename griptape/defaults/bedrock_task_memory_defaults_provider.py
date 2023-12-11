from __future__ import annotations

from attr import define, field

from griptape.defaults import BaseTaskMemoryDefaultsProvider
from griptape.drivers import (
    AmazonBedrockPromptDriver,
    BaseEmbeddingDriver,
    BasePromptDriver,
    BedrockTitanEmbeddingDriver,
    BedrockTitanPromptModelDriver,
)


@define
class BedrockTaskMemoryDefaultsProvider(BaseTaskMemoryDefaultsProvider):
    query_engine_prompt_driver: BasePromptDriver = field(
        default=AmazonBedrockPromptDriver(
            model="amazon.titan-text-express-v1", prompt_model_driver=BedrockTitanPromptModelDriver()
        )
    )
    query_engine_embedding_driver: BaseEmbeddingDriver = field(default=BedrockTitanEmbeddingDriver())
    summary_engine_prompt_driver: BasePromptDriver = field(
        default=AmazonBedrockPromptDriver(
            model="amazon.titan-text-express-v1", prompt_model_driver=BedrockTitanPromptModelDriver()
        )
    )
    csv_extraction_engine_prompt_driver: BasePromptDriver = field(
        default=AmazonBedrockPromptDriver(
            model="amazon.titan-text-express-v1", prompt_model_driver=BedrockTitanPromptModelDriver()
        )
    )
    json_extraction_engine_prompt_driver: BasePromptDriver = field(
        default=AmazonBedrockPromptDriver(
            model="amazon.titan-text-express-v1", prompt_model_driver=BedrockTitanPromptModelDriver()
        )
    )
