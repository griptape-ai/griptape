from griptape.utils.deprecation import DeprecationModuleWrapper
import sys

# Lazy loading mapping: maps class names to their import paths
_DRIVER_IMPORTS = {
    # Base Classes
    "BasePromptDriver": ("griptape.drivers.prompt", "BasePromptDriver"),
    "BaseConversationMemoryDriver": ("griptape.drivers.memory.conversation", "BaseConversationMemoryDriver"),
    "BaseEmbeddingDriver": ("griptape.drivers.embedding", "BaseEmbeddingDriver"),
    "BaseVectorStoreDriver": ("griptape.drivers.vector", "BaseVectorStoreDriver"),
    "BaseSqlDriver": ("griptape.drivers.sql", "BaseSqlDriver"),
    "BaseImageGenerationModelDriver": ("griptape.drivers.image_generation_model", "BaseImageGenerationModelDriver"),
    "BaseDiffusionImageGenerationPipelineDriver": (
        "griptape.drivers.image_generation_pipeline",
        "BaseDiffusionImageGenerationPipelineDriver",
    ),
    "BaseImageGenerationDriver": ("griptape.drivers.image_generation", "BaseImageGenerationDriver"),
    "BaseMultiModelImageGenerationDriver": ("griptape.drivers.image_generation", "BaseMultiModelImageGenerationDriver"),
    "BaseWebScraperDriver": ("griptape.drivers.web_scraper", "BaseWebScraperDriver"),
    "BaseWebSearchDriver": ("griptape.drivers.web_search", "BaseWebSearchDriver"),
    "BaseEventListenerDriver": ("griptape.drivers.event_listener", "BaseEventListenerDriver"),
    "BaseFileManagerDriver": ("griptape.drivers.file_manager", "BaseFileManagerDriver"),
    "BaseRerankDriver": ("griptape.drivers.rerank", "BaseRerankDriver"),
    "BaseRulesetDriver": ("griptape.drivers.ruleset", "BaseRulesetDriver"),
    "BaseTextToSpeechDriver": ("griptape.drivers.text_to_speech", "BaseTextToSpeechDriver"),
    "BaseStructureRunDriver": ("griptape.drivers.structure_run", "BaseStructureRunDriver"),
    "BaseAudioTranscriptionDriver": ("griptape.drivers.audio_transcription", "BaseAudioTranscriptionDriver"),
    "BaseObservabilityDriver": ("griptape.drivers.observability", "BaseObservabilityDriver"),
    "BaseAssistantDriver": ("griptape.drivers.assistant", "BaseAssistantDriver"),
    # Prompt Drivers
    "OpenAiChatPromptDriver": ("griptape.drivers.prompt.openai", "OpenAiChatPromptDriver"),
    "AzureOpenAiChatPromptDriver": ("griptape.drivers.prompt.openai", "AzureOpenAiChatPromptDriver"),
    "CoherePromptDriver": ("griptape.drivers.prompt.cohere", "CoherePromptDriver"),
    "HuggingFacePipelinePromptDriver": (
        "griptape.drivers.prompt.huggingface_pipeline",
        "HuggingFacePipelinePromptDriver",
    ),
    "HuggingFaceHubPromptDriver": ("griptape.drivers.prompt.huggingface_hub", "HuggingFaceHubPromptDriver"),
    "AnthropicPromptDriver": ("griptape.drivers.prompt.anthropic", "AnthropicPromptDriver"),
    "AmazonSageMakerJumpstartPromptDriver": (
        "griptape.drivers.prompt.amazon_sagemaker_jumpstart",
        "AmazonSageMakerJumpstartPromptDriver",
    ),
    "AmazonBedrockPromptDriver": ("griptape.drivers.prompt.amazon_bedrock", "AmazonBedrockPromptDriver"),
    "GooglePromptDriver": ("griptape.drivers.prompt.google", "GooglePromptDriver"),
    "DummyPromptDriver": ("griptape.drivers.prompt.dummy", "DummyPromptDriver"),
    "OllamaPromptDriver": ("griptape.drivers.prompt.ollama", "OllamaPromptDriver"),
    "GrokPromptDriver": ("griptape.drivers.prompt.grok", "GrokPromptDriver"),
    "GriptapeCloudPromptDriver": ("griptape.drivers.prompt.griptape_cloud", "GriptapeCloudPromptDriver"),
    "PerplexityPromptDriver": ("griptape.drivers.prompt.perplexity", "PerplexityPromptDriver"),
    # Conversation Memory Drivers
    "LocalConversationMemoryDriver": ("griptape.drivers.memory.conversation.local", "LocalConversationMemoryDriver"),
    "AmazonDynamoDbConversationMemoryDriver": (
        "griptape.drivers.memory.conversation.amazon_dynamodb",
        "AmazonDynamoDbConversationMemoryDriver",
    ),
    "RedisConversationMemoryDriver": ("griptape.drivers.memory.conversation.redis", "RedisConversationMemoryDriver"),
    "GriptapeCloudConversationMemoryDriver": (
        "griptape.drivers.memory.conversation.griptape_cloud",
        "GriptapeCloudConversationMemoryDriver",
    ),
    # Embedding Drivers
    "OpenAiEmbeddingDriver": ("griptape.drivers.embedding.openai", "OpenAiEmbeddingDriver"),
    "AzureOpenAiEmbeddingDriver": ("griptape.drivers.embedding.openai", "AzureOpenAiEmbeddingDriver"),
    "AmazonSageMakerJumpstartEmbeddingDriver": (
        "griptape.drivers.embedding.amazon_sagemaker_jumpstart",
        "AmazonSageMakerJumpstartEmbeddingDriver",
    ),
    "AmazonBedrockTitanEmbeddingDriver": (
        "griptape.drivers.embedding.amazon_bedrock",
        "AmazonBedrockTitanEmbeddingDriver",
    ),
    "AmazonBedrockCohereEmbeddingDriver": (
        "griptape.drivers.embedding.amazon_bedrock",
        "AmazonBedrockCohereEmbeddingDriver",
    ),
    "VoyageAiEmbeddingDriver": ("griptape.drivers.embedding.voyageai", "VoyageAiEmbeddingDriver"),
    "HuggingFaceHubEmbeddingDriver": ("griptape.drivers.embedding.huggingface_hub", "HuggingFaceHubEmbeddingDriver"),
    "GoogleEmbeddingDriver": ("griptape.drivers.embedding.google", "GoogleEmbeddingDriver"),
    "DummyEmbeddingDriver": ("griptape.drivers.embedding.dummy", "DummyEmbeddingDriver"),
    "CohereEmbeddingDriver": ("griptape.drivers.embedding.cohere", "CohereEmbeddingDriver"),
    "OllamaEmbeddingDriver": ("griptape.drivers.embedding.ollama", "OllamaEmbeddingDriver"),
    # Vector Store Drivers
    "LocalVectorStoreDriver": ("griptape.drivers.vector.local", "LocalVectorStoreDriver"),
    "PineconeVectorStoreDriver": ("griptape.drivers.vector.pinecone", "PineconeVectorStoreDriver"),
    "MarqoVectorStoreDriver": ("griptape.drivers.vector.marqo", "MarqoVectorStoreDriver"),
    "MongoDbAtlasVectorStoreDriver": ("griptape.drivers.vector.mongodb_atlas", "MongoDbAtlasVectorStoreDriver"),
    "RedisVectorStoreDriver": ("griptape.drivers.vector.redis", "RedisVectorStoreDriver"),
    "OpenSearchVectorStoreDriver": ("griptape.drivers.vector.opensearch", "OpenSearchVectorStoreDriver"),
    "AmazonOpenSearchVectorStoreDriver": (
        "griptape.drivers.vector.amazon_opensearch",
        "AmazonOpenSearchVectorStoreDriver",
    ),
    "PgVectorVectorStoreDriver": ("griptape.drivers.vector.pgvector", "PgVectorVectorStoreDriver"),
    "AzureMongoDbVectorStoreDriver": ("griptape.drivers.vector.azure_mongodb", "AzureMongoDbVectorStoreDriver"),
    "DummyVectorStoreDriver": ("griptape.drivers.vector.dummy", "DummyVectorStoreDriver"),
    "QdrantVectorStoreDriver": ("griptape.drivers.vector.qdrant", "QdrantVectorStoreDriver"),
    "AstraDbVectorStoreDriver": ("griptape.drivers.vector.astradb", "AstraDbVectorStoreDriver"),
    "GriptapeCloudVectorStoreDriver": ("griptape.drivers.vector.griptape_cloud", "GriptapeCloudVectorStoreDriver"),
    "PgAiKnowledgeBaseVectorStoreDriver": ("griptape.drivers.vector.pgai", "PgAiKnowledgeBaseVectorStoreDriver"),
    # SQL Drivers
    "SqlDriver": ("griptape.drivers.sql.sql_driver", "SqlDriver"),
    "AmazonRedshiftSqlDriver": ("griptape.drivers.sql.amazon_redshift", "AmazonRedshiftSqlDriver"),
    "SnowflakeSqlDriver": ("griptape.drivers.sql.snowflake", "SnowflakeSqlDriver"),
    # Image Generation Model Drivers
    "BedrockStableDiffusionImageGenerationModelDriver": (
        "griptape.drivers.image_generation_model.bedrock_stable_diffusion",
        "BedrockStableDiffusionImageGenerationModelDriver",
    ),
    "BedrockTitanImageGenerationModelDriver": (
        "griptape.drivers.image_generation_model.bedrock_titan",
        "BedrockTitanImageGenerationModelDriver",
    ),
    # Image Generation Pipeline Drivers
    "StableDiffusion3ImageGenerationPipelineDriver": (
        "griptape.drivers.image_generation_pipeline.stable_diffusion_3",
        "StableDiffusion3ImageGenerationPipelineDriver",
    ),
    "StableDiffusion3Img2ImgImageGenerationPipelineDriver": (
        "griptape.drivers.image_generation_pipeline.stable_diffusion_3_img_2_img",
        "StableDiffusion3Img2ImgImageGenerationPipelineDriver",
    ),
    "StableDiffusion3ControlNetImageGenerationPipelineDriver": (
        "griptape.drivers.image_generation_pipeline.stable_diffusion_3_controlnet",
        "StableDiffusion3ControlNetImageGenerationPipelineDriver",
    ),
    # Image Generation Drivers
    "OpenAiImageGenerationDriver": ("griptape.drivers.image_generation.openai", "OpenAiImageGenerationDriver"),
    "AzureOpenAiImageGenerationDriver": (
        "griptape.drivers.image_generation.openai",
        "AzureOpenAiImageGenerationDriver",
    ),
    "LeonardoImageGenerationDriver": ("griptape.drivers.image_generation.leonardo", "LeonardoImageGenerationDriver"),
    "AmazonBedrockImageGenerationDriver": (
        "griptape.drivers.image_generation.amazon_bedrock",
        "AmazonBedrockImageGenerationDriver",
    ),
    "DummyImageGenerationDriver": ("griptape.drivers.image_generation.dummy", "DummyImageGenerationDriver"),
    "HuggingFacePipelineImageGenerationDriver": (
        "griptape.drivers.image_generation.huggingface_pipeline",
        "HuggingFacePipelineImageGenerationDriver",
    ),
    "GriptapeCloudImageGenerationDriver": (
        "griptape.drivers.image_generation.griptape_cloud",
        "GriptapeCloudImageGenerationDriver",
    ),
    # Web Scraper Drivers
    "TrafilaturaWebScraperDriver": ("griptape.drivers.web_scraper.trafilatura", "TrafilaturaWebScraperDriver"),
    "MarkdownifyWebScraperDriver": ("griptape.drivers.web_scraper.markdownify", "MarkdownifyWebScraperDriver"),
    "ProxyWebScraperDriver": ("griptape.drivers.web_scraper.proxy", "ProxyWebScraperDriver"),
    # Web Search Drivers
    "GoogleWebSearchDriver": ("griptape.drivers.web_search.google", "GoogleWebSearchDriver"),
    "DuckDuckGoWebSearchDriver": ("griptape.drivers.web_search.duck_duck_go", "DuckDuckGoWebSearchDriver"),
    "ExaWebSearchDriver": ("griptape.drivers.web_search.exa", "ExaWebSearchDriver"),
    "TavilyWebSearchDriver": ("griptape.drivers.web_search.tavily", "TavilyWebSearchDriver"),
    "PerplexityWebSearchDriver": ("griptape.drivers.web_search.perplexity", "PerplexityWebSearchDriver"),
    # Event Listener Drivers
    "AmazonSqsEventListenerDriver": ("griptape.drivers.event_listener.amazon_sqs", "AmazonSqsEventListenerDriver"),
    "WebhookEventListenerDriver": ("griptape.drivers.event_listener.webhook", "WebhookEventListenerDriver"),
    "AwsIotCoreEventListenerDriver": ("griptape.drivers.event_listener.aws_iot_core", "AwsIotCoreEventListenerDriver"),
    "GriptapeCloudEventListenerDriver": (
        "griptape.drivers.event_listener.griptape_cloud",
        "GriptapeCloudEventListenerDriver",
    ),
    "PusherEventListenerDriver": ("griptape.drivers.event_listener.pusher", "PusherEventListenerDriver"),
    # File Manager Drivers
    "LocalFileManagerDriver": ("griptape.drivers.file_manager.local", "LocalFileManagerDriver"),
    "AmazonS3FileManagerDriver": ("griptape.drivers.file_manager.amazon_s3", "AmazonS3FileManagerDriver"),
    "GriptapeCloudFileManagerDriver": (
        "griptape.drivers.file_manager.griptape_cloud",
        "GriptapeCloudFileManagerDriver",
    ),
    # Rerank Drivers
    "CohereRerankDriver": ("griptape.drivers.rerank.cohere", "CohereRerankDriver"),
    "LocalRerankDriver": ("griptape.drivers.rerank.local", "LocalRerankDriver"),
    # Ruleset Drivers
    "LocalRulesetDriver": ("griptape.drivers.ruleset.local", "LocalRulesetDriver"),
    "GriptapeCloudRulesetDriver": ("griptape.drivers.ruleset.griptape_cloud", "GriptapeCloudRulesetDriver"),
    # Text-to-Speech Drivers
    "DummyTextToSpeechDriver": ("griptape.drivers.text_to_speech.dummy", "DummyTextToSpeechDriver"),
    "ElevenLabsTextToSpeechDriver": ("griptape.drivers.text_to_speech.elevenlabs", "ElevenLabsTextToSpeechDriver"),
    "OpenAiTextToSpeechDriver": ("griptape.drivers.text_to_speech.openai", "OpenAiTextToSpeechDriver"),
    "AzureOpenAiTextToSpeechDriver": ("griptape.drivers.text_to_speech.openai", "AzureOpenAiTextToSpeechDriver"),
    # Structure Run Drivers
    "GriptapeCloudStructureRunDriver": (
        "griptape.drivers.structure_run.griptape_cloud",
        "GriptapeCloudStructureRunDriver",
    ),
    "LocalStructureRunDriver": ("griptape.drivers.structure_run.local", "LocalStructureRunDriver"),
    # Audio Transcription Drivers
    "DummyAudioTranscriptionDriver": (
        "griptape.drivers.audio_transcription.dummy",
        "DummyAudioTranscriptionDriver",
    ),
    "OpenAiAudioTranscriptionDriver": (
        "griptape.drivers.audio_transcription.openai",
        "OpenAiAudioTranscriptionDriver",
    ),
    # Observability Drivers
    "NoOpObservabilityDriver": ("griptape.drivers.observability.no_op", "NoOpObservabilityDriver"),
    "OpenTelemetryObservabilityDriver": (
        "griptape.drivers.observability.open_telemetry",
        "OpenTelemetryObservabilityDriver",
    ),
    "GriptapeCloudObservabilityDriver": (
        "griptape.drivers.observability.griptape_cloud",
        "GriptapeCloudObservabilityDriver",
    ),
    "DatadogObservabilityDriver": ("griptape.drivers.observability.datadog", "DatadogObservabilityDriver"),
    # Assistant Drivers
    "GriptapeCloudAssistantDriver": ("griptape.drivers.assistant.griptape_cloud", "GriptapeCloudAssistantDriver"),
    "OpenAiAssistantDriver": ("griptape.drivers.assistant.openai", "OpenAiAssistantDriver"),
}


def __getattr__(name: str):
    """Lazily import drivers only when accessed."""
    if name in _DRIVER_IMPORTS:
        module_path, class_name = _DRIVER_IMPORTS[name]
        from importlib import import_module

        module = import_module(module_path)
        driver_class = getattr(module, class_name)
        # Cache the imported class in the module's namespace
        globals()[name] = driver_class
        return driver_class
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    """Support for dir() and tab completion."""
    return list(_DRIVER_IMPORTS.keys())


__all__ = [
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
    "BaseAssistantDriver",
    "BaseAudioTranscriptionDriver",
    "BaseConversationMemoryDriver",
    "BaseDiffusionImageGenerationPipelineDriver",
    "BaseEmbeddingDriver",
    "BaseEventListenerDriver",
    "BaseFileManagerDriver",
    "BaseImageGenerationDriver",
    "BaseImageGenerationModelDriver",
    "BaseMultiModelImageGenerationDriver",
    "BaseObservabilityDriver",
    "BasePromptDriver",
    "BaseRerankDriver",
    "BaseRulesetDriver",
    "BaseSqlDriver",
    "BaseStructureRunDriver",
    "BaseTextToSpeechDriver",
    "BaseVectorStoreDriver",
    "BaseWebScraperDriver",
    "BaseWebSearchDriver",
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
