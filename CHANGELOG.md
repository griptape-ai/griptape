# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.22.0] - 2024-01-11

### Added
- `PromptImageGenerationEngine` for generating images from text prompts. 
- `VariationImageGenerationEngine` for generating variations of an input image according to a text prompt.
- `InpaintingImageGenerationEngine` for modifying an input image according to a text prompt within the bounds of a mask defined by a mask image. 
- `OutpaintingImageGenerationEngine` for modifying an input image according to a text prompt outside the bounds of a mask defined by a mask image.
- `ImageArtifact` for storing image data; used heavily by the image Engines, Tasks, and Drivers.
- `ImageLoader` for loading images files into `ImageArtifact`s.
- Support for all Tokenizers in `OpenAiChatPromptDriver`, enabling OpenAi drop-in clients such as TogetherAi.
- `AmazonSageMakerEmbeddingDriver` for using Amazon SageMaker to generate embeddings. Thanks @KaushikIyer16!
- Claude 2.1 support in `AnthropicPromptDriver` and `AmazonBedrockPromptDriver` via `BedrockClaudePromptModelDriver`.
- `CodeExecutionTask` for running Python functions without an LLM.
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
- Improve system prompt generation with Claude 2.0.
- Improve integration test coverage.
- `BaseTextInputTask` to accept a `str`, `TextArtifact` or callable returning a `TextArtifact`.
