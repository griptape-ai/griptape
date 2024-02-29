# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

## [0.23.0] - 2024-02-26

### Added 
- Image-to-image generation support for OpenAi Dall-E 2 model.
- Image tools support loading artifacts from memory.
- `AzureMongoDbVectorStoreDriver` for using CosmosDB with MongoDB vCore API.
- `vector_path` field on `MongoDbAtlasVectorStoreDriver`.
- `LeonardoImageGenerationDriver` supports image to image generation.
- `OpenAiStructureConfig` for providing Structures with all OpenAi Driver configuration. 
- `AmazonBedrockStructureConfig` for providing Structures with all Amazon Bedrock Driver configuration. 
- `StructureConfig` for building your own Structure configuration.
- `JsonExtractionTask` for convenience over using `ExtractionTask` with a `JsonExtractionEngine`.
- `CsvExtractionTask` for convenience over using `ExtractionTask` with a `CsvExtractionEngine`.
- `OpenAiVisionImageQueryDriver` to support queries on images using OpenAI's Vision model.
- `ImageQueryClient` allowing an Agent to make queries on images on disk or in Task Memory.
- `ImageQueryTask` and `ImageQueryEngine`.

### Fixed 
- `BedrockStableDiffusionImageGenerationModelDriver` request parameters for SDXLv1.
- `BedrockStableDiffusionImageGenerationModelDriver` correctly handles the CONTENT_FILTERED response case.

### Changed
- **BREAKING**: Make `index_name` on `MongoDbAtlasVectorStoreDriver` a required field.
- **BREAKING**: Remove `create_index()` from `MarqoVectorStoreDriver`, `OpenSearchVectorStoreDriver`, `PineconeVectorStoreDriver`, `RedisVectorStoreDriver`.
- **BREAKING**: `ImageLoader().load()` now accepts image bytes instead of a file path.
- Deprecated `Structure.prompt_driver` in favor of `Structure.config.global_drivers.prompt_driver`.
- Deprecated `Structure.embedding_driver` in favor of `Structure.config.global_drivers.embedding_driver`.
- Deprecated `Structure.stream` in favor of `Structure.config.global_drivers.prompt_driver.stream`.
- `TextSummaryTask.summary_engine` now defaults to a `PromptSummaryEngine` with a Prompt Driver default of `Structure.config.global_drivers.prompt_driver`.
- `TextQueryTask.query_engine` now defaults to a `VectorQueryEngine` with a Prompt Driver default of `Structure.config.global_drivers.prompt_driver` and Vector Store Driver default of `Structure.config.global_drivers.vector_store_driver`.
- `PromptImageGenerationTask.image_generation_engine` now defaults to a `PromptImageGenerationEngine` with an Image Generation Driver default of `Structure.config.global_drivers.image_generation_driver`.
- `VariationImageGenerationTask.image_generation_engine` now defaults to a `VariationImageGenerationEngine` with an Image Generation Driver default of `Structure.config.global_drivers.image_generation_driver`.
- `InpaintingImageGenerationTask.image_generation_engine` now defaults to an `InpaintingImageGenerationEngine` with an Image Generation Driver default of `Structure.config.global_drivers.image_generation_driver`.
- `OutpaintingImageGenerationTask.image_generation_engine` now defaults to an `OutpaintingImageGenerationEngine` with an Image Generation Driver default of `Structure.config.global_drivers.image_generation_driver`.

## [0.22.3] - 2024-01-22

### Fixed
- `ToolkitTask`'s user subtask prompt occasionally causing the Task to end prematurely.

## [0.22.2] - 2024-01-18

### Fixed
- `ToolkitTask`'s user subtask prompt occassionally causing a loop with Chain of Thought.

### Security
- Updated stale dependencies [CVE-2023-50447, CVE-2024-22195, and CVE-2023-36464]

## [0.22.1] - 2024-01-12

### Fixed
- Action Subtasks incorrectly outputting the Task input after failing to follow the ReAct prompt.

## [0.22.0] - 2024-01-11

### Added
- `PromptImageGenerationEngine` for generating images from text prompts. 
- `VariationImageGenerationEngine` for generating variations of an input image according to a text prompt.
- `InpaintingImageGenerationEngine` for modifying an input image according to a text prompt within the bounds of a mask defined by a mask image. 
- `OutpaintingImageGenerationEngine` for modifying an input image according to a text prompt outside the bounds of a mask defined by a mask image.

- `PromptImageGenerationClient` for enabling an LLM to use the `PromptImageGenerationEngine`.
- `VariationImageGenerationClient` for enabling an LLM to use the `VariationImageGenerationEngine`.
- `InpaintingImageGenerationClient` for enabling an LLM to use the `InpaintingImageGenerationEngine`.
- `OutpaintingImageGenerationClient` for enabling an LLM to use the `OutpaintingImageGenerationEngine`.

- `OpenAiImageGenerationDriver` for use with OpenAI's image generation models.
- `LeonardoImageGenerationDriver` for use with Leonoaro AI's image generation models.
- `AmazonBedrockImageGenerationDriver` for use with Amazon Bedrock's image generation models; requires a Image Generation Model Driver.
- `BedrockTitanImageGenerationModelDriver` for use with Amazon Bedrock's Titan image generation.

- `ImageArtifact` for storing image data; used heavily by the image Engines, Tasks, and Drivers.
- `ImageLoader` for loading images files into `ImageArtifact`s.

- Support for all Tokenizers in `OpenAiChatPromptDriver`, enabling OpenAI drop-in clients such as Together AI.
- `AmazonSageMakerEmbeddingDriver` for using Amazon SageMaker to generate embeddings. Thanks @KaushikIyer16!
- Claude 2.1 support in `AnthropicPromptDriver` and `AmazonBedrockPromptDriver` via `BedrockClaudePromptModelDriver`.
- `CodeExecutionTask` for executing code as a Task without the need for an LLM.
- `BedrockLlamaPromptModelDriver` for using Llama models on Amazon Bedrock.


### Fixed
- `MongoDbAtlasVectorStore` namespace not being used properly when querying. 
- Miscellaneous type errors throughout the codebase.
- Remove unused section from `ToolTask` system prompt template.
- Structure execution args being cleared after run, preventing inspection of the Structure's `input_task`'s `input`.
- Unhandled `SqlClient` exception. Thanks @michal-repo!

### Changed
- **BREAKING**: Rename `input_template` field to `input` in Tasks that take a text input.
- **BREAKING**: Rename `BedrockTitanEmbeddingDriver` to `AmazonBedrockTitanEmbeddingDriver`.
- **BREAKING**: Rename `AmazonBedrockStableDiffusionImageGenerationModelDriver` to `BedrockStableDiffusionImageGenerationModelDriver`.
- **BREAKING**: Rename `AmazonBedrockTitanImageGenerationModelDriver` to `BedrockTitanImageGenerationModelDriver`.
- **BREAKING**: Rename `ImageGenerationTask` to `PromptImageGenerationTask`.
- **BREAKING**: Rename `ImageGenerationEngine` to `PromptImageGenerationEngine`.
- **BREAKING**: Rename `ImageGenerationTool` to `PromptImageGenerationClient`.
- Improve system prompt generation with Claude 2.0.
- Improve integration test coverage.
- `BaseTextInputTask` to accept a `str`, `TextArtifact` or callable returning a `TextArtifact`.
