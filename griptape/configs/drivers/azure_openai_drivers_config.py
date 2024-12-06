from __future__ import annotations

from typing import Callable, Optional

from attrs import define, field

from griptape.configs.drivers import DriversConfig
from griptape.drivers import (
    AzureOpenAiChatPromptDriver,
    AzureOpenAiEmbeddingDriver,
    AzureOpenAiImageGenerationDriver,
    AzureOpenAiTextToSpeechDriver,
    LocalVectorStoreDriver,
)
from griptape.utils.decorators import lazy_property


@define
class AzureOpenAiDriversConfig(DriversConfig):
    """Azure OpenAI Drivers Configuration.

    Attributes:
        azure_endpoint: The endpoint for the Azure OpenAI instance.
        azure_ad_token: An optional Azure Active Directory token.
        azure_ad_token_provider: An optional Azure Active Directory token provider.
        api_key: An optional Azure API key.
        prompt_driver: An Azure OpenAI Chat Prompt Driver.
        image_generation_driver: An Azure OpenAI Image Generation Driver.
        embedding_driver: An Azure OpenAI Embedding Driver.
        vector_store_driver: A Local Vector Store Driver.
    """

    azure_endpoint: str = field(kw_only=True, metadata={"serializable": True})
    azure_ad_token: Optional[str] = field(kw_only=True, default=None, metadata={"serializable": False})
    azure_ad_token_provider: Optional[Callable[[], str]] = field(
        kw_only=True,
        default=None,
        metadata={"serializable": False},
    )
    api_key: Optional[str] = field(kw_only=True, default=None, metadata={"serializable": False})

    @lazy_property()
    def prompt_driver(self) -> AzureOpenAiChatPromptDriver:
        return AzureOpenAiChatPromptDriver(
            model="gpt-4o",
            azure_endpoint=self.azure_endpoint,
            api_key=self.api_key,
            azure_ad_token=self.azure_ad_token,
            azure_ad_token_provider=self.azure_ad_token_provider,
        )

    @lazy_property()
    def embedding_driver(self) -> AzureOpenAiEmbeddingDriver:
        return AzureOpenAiEmbeddingDriver(
            model="text-embedding-3-small",
            azure_endpoint=self.azure_endpoint,
            api_key=self.api_key,
            azure_ad_token=self.azure_ad_token,
            azure_ad_token_provider=self.azure_ad_token_provider,
        )

    @lazy_property()
    def image_generation_driver(self) -> AzureOpenAiImageGenerationDriver:
        return AzureOpenAiImageGenerationDriver(
            model="dall-e-2",
            azure_endpoint=self.azure_endpoint,
            api_key=self.api_key,
            azure_ad_token=self.azure_ad_token,
            azure_ad_token_provider=self.azure_ad_token_provider,
            image_size="512x512",
        )

    @lazy_property()
    def vector_store_driver(self) -> LocalVectorStoreDriver:
        return LocalVectorStoreDriver(
            embedding_driver=AzureOpenAiEmbeddingDriver(
                model="text-embedding-3-small",
                azure_endpoint=self.azure_endpoint,
                api_key=self.api_key,
                azure_ad_token=self.azure_ad_token,
                azure_ad_token_provider=self.azure_ad_token_provider,
            )
        )

    @lazy_property()
    def text_to_speech_driver(self) -> AzureOpenAiTextToSpeechDriver:
        return AzureOpenAiTextToSpeechDriver(
            model="tts",
            azure_endpoint=self.azure_endpoint,
            api_key=self.api_key,
            azure_ad_token=self.azure_ad_token,
            azure_ad_token_provider=self.azure_ad_token_provider,
        )
