import sys
import importlib
import importlib.util
from typing import Any

from griptape.utils.deprecation import DeprecationModuleWrapper
from griptape.common._lazy_loader import find_driver_module, discover_all_drivers

# Import base classes eagerly (they're always needed for type checking and inheritance)
from .prompt import BasePromptDriver
from .memory.conversation import BaseConversationMemoryDriver
from .embedding import BaseEmbeddingDriver
from .vector import BaseVectorStoreDriver
from .sql import BaseSqlDriver
from .image_generation_model import BaseImageGenerationModelDriver
from .image_generation_pipeline import BaseDiffusionImageGenerationPipelineDriver
from .image_generation import BaseImageGenerationDriver, BaseMultiModelImageGenerationDriver
from .web_scraper import BaseWebScraperDriver
from .web_search import BaseWebSearchDriver
from .event_listener import BaseEventListenerDriver
from .file_manager import BaseFileManagerDriver
from .rerank import BaseRerankDriver
from .ruleset import BaseRulesetDriver
from .text_to_speech import BaseTextToSpeechDriver
from .structure_run import BaseStructureRunDriver
from .audio_transcription import BaseAudioTranscriptionDriver
from .observability import BaseObservabilityDriver
from .assistant import BaseAssistantDriver


def __getattr__(name: str) -> Any:
    """Lazy-load driver classes on first access.

    This function is called when an attribute is accessed that doesn't exist in the module's namespace.
    It uses pkgutil to search the driver directory tree and find where the class is actually defined.

    Args:
        name: The name of the driver class to import

    Returns:
        The driver class

    Raises:
        AttributeError: If the driver class cannot be found
    """
    if not name.endswith("Driver"):
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    # Find the module containing this driver
    module_path = find_driver_module(name)

    if module_path is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    # Import and cache the driver
    try:
        module = importlib.import_module(module_path)
        driver_class = getattr(module, name)
        # Cache for future access
        globals()[name] = driver_class
        return driver_class
    except (ImportError, AttributeError) as e:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from e


def __dir__() -> list[str]:
    """Support dir() and IDE autocomplete by listing all available drivers.

    Returns:
        List of all available names in this module (base classes + discovered drivers)
    """
    # Combine eagerly loaded base classes with dynamically discovered drivers
    base_names = [name for name in globals() if not name.startswith("_")]
    discovered = discover_all_drivers()
    return sorted(set(base_names + discovered))


__all__ = [
    # Base classes (eagerly loaded)
    "BasePromptDriver",
    "BaseConversationMemoryDriver",
    "BaseEmbeddingDriver",
    "BaseVectorStoreDriver",
    "BaseSqlDriver",
    "BaseImageGenerationModelDriver",
    "BaseDiffusionImageGenerationPipelineDriver",
    "BaseImageGenerationDriver",
    "BaseMultiModelImageGenerationDriver",
    "BaseWebScraperDriver",
    "BaseWebSearchDriver",
    "BaseEventListenerDriver",
    "BaseFileManagerDriver",
    "BaseRerankDriver",
    "BaseRulesetDriver",
    "BaseTextToSpeechDriver",
    "BaseStructureRunDriver",
    "BaseAudioTranscriptionDriver",
    "BaseObservabilityDriver",
    "BaseAssistantDriver",
    # All concrete drivers are available via lazy loading
    # (listing them all here for from X import * compatibility)
    "AmazonBedrockCohereEmbeddingDriver",
    "AmazonBedrockImageGenerationDriver",
    "AmazonBedrockPromptDriver",
    "AmazonBedrockTitanEmbeddingDriver",
    "AmazonDynamoDbConversationMemoryDriver",
    "AmazonOpenSearchVectorStoreDriver",
    "AmazonRedshiftSqlDriver",
    "AmazonS3FileManagerDriver",
    "AmazonSageMakerJumpstartEmbeddingDriver",
    "AmazonSageMakerJumpstartPromptDriver",
    "AmazonSqsEventListenerDriver",
    "AnthropicPromptDriver",
    "AstraDbVectorStoreDriver",
    "AwsIotCoreEventListenerDriver",
    "AzureMongoDbVectorStoreDriver",
    "AzureOpenAiChatPromptDriver",
    "AzureOpenAiEmbeddingDriver",
    "AzureOpenAiImageGenerationDriver",
    "AzureOpenAiTextToSpeechDriver",
    "BedrockStableDiffusionImageGenerationModelDriver",
    "BedrockTitanImageGenerationModelDriver",
    "CohereEmbeddingDriver",
    "CoherePromptDriver",
    "CohereRerankDriver",
    "DatadogObservabilityDriver",
    "DuckDuckGoWebSearchDriver",
    "DummyAudioTranscriptionDriver",
    "DummyEmbeddingDriver",
    "DummyImageGenerationDriver",
    "DummyPromptDriver",
    "DummyTextToSpeechDriver",
    "DummyVectorStoreDriver",
    "ElevenLabsTextToSpeechDriver",
    "ExaWebSearchDriver",
    "GoogleEmbeddingDriver",
    "GooglePromptDriver",
    "GoogleWebSearchDriver",
    "GriptapeCloudAssistantDriver",
    "GriptapeCloudConversationMemoryDriver",
    "GriptapeCloudEventListenerDriver",
    "GriptapeCloudFileManagerDriver",
    "GriptapeCloudImageGenerationDriver",
    "GriptapeCloudObservabilityDriver",
    "GriptapeCloudPromptDriver",
    "GriptapeCloudRulesetDriver",
    "GriptapeCloudStructureRunDriver",
    "GriptapeCloudVectorStoreDriver",
    "GrokPromptDriver",
    "HuggingFaceHubEmbeddingDriver",
    "HuggingFaceHubPromptDriver",
    "HuggingFacePipelineImageGenerationDriver",
    "HuggingFacePipelinePromptDriver",
    "LeonardoImageGenerationDriver",
    "LocalConversationMemoryDriver",
    "LocalFileManagerDriver",
    "LocalRerankDriver",
    "LocalRulesetDriver",
    "LocalStructureRunDriver",
    "LocalVectorStoreDriver",
    "MarkdownifyWebScraperDriver",
    "MarqoVectorStoreDriver",
    "MongoDbAtlasVectorStoreDriver",
    "NoOpObservabilityDriver",
    "OllamaEmbeddingDriver",
    "OllamaPromptDriver",
    "OpenAiAssistantDriver",
    "OpenAiAudioTranscriptionDriver",
    "OpenAiChatPromptDriver",
    "OpenAiEmbeddingDriver",
    "OpenAiImageGenerationDriver",
    "OpenAiTextToSpeechDriver",
    "OpenSearchVectorStoreDriver",
    "OpenTelemetryObservabilityDriver",
    "PerplexityPromptDriver",
    "PerplexityWebSearchDriver",
    "PgAiKnowledgeBaseVectorStoreDriver",
    "PgVectorVectorStoreDriver",
    "PineconeVectorStoreDriver",
    "ProxyWebScraperDriver",
    "PusherEventListenerDriver",
    "QdrantVectorStoreDriver",
    "RedisConversationMemoryDriver",
    "RedisVectorStoreDriver",
    "SnowflakeSqlDriver",
    "SqlDriver",
    "StableDiffusion3ControlNetImageGenerationPipelineDriver",
    "StableDiffusion3ImageGenerationPipelineDriver",
    "StableDiffusion3Img2ImgImageGenerationPipelineDriver",
    "TavilyWebSearchDriver",
    "TrafilaturaWebScraperDriver",
    "VoyageAiEmbeddingDriver",
    "WebhookEventListenerDriver",
]


sys.modules[__name__] = DeprecationModuleWrapper(
    sys.modules[__name__],
    deprecation_message="Importing from `griptape.drivers` is deprecated and will be removed in a future release. "
    "Please import from the provider-specific package instead.\n"
    "e.g., `from griptape.drivers import OpenAiChatPromptDriver` -> `from griptape.drivers.prompt.openai import OpenAiChatPromptDriver`",
)
