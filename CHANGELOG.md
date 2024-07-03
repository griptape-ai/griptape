# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added
- `RagEngine` is an abstraction for implementing modular RAG pipelines.
  - `RagContext` is a container object for passing around RAG context. 
  - RAG stages:
    - `QueryRagStage` for parsing and expanding queries.
    - `RetrievalRagStage` for retrieving content.
    - `ResponseRagStage` for augmenting and generating outputs.
  - RAG modules:
    - Retrieval:
      - `VectorStoreRetrievalRagModule` for retrieving text chunks from vector stores.
      - `TextChunksRerankRagModule` for re-ranking retrieved results.
    - Response:
      - `MetadataBeforeResponseRagModule` for appending metadata.
      - `RulesetsBeforeResponseRagModule` for appending rulesets.
      - `PromptResponseRagModule` for generating responses based on retrieved text chunks.
      - `TextChunksResponseRagModule` for responding with retrieved text chunks.
- `RagClient` tool for exposing `RagEngines` to LLM agents.
- `RagTask` task for including `RagEngines` in any structure.
- Rerank drivers:
  - `CohereRerankDriver` for using the Cohere rerank API.
- `utils.execute_futures_list()` for executing a list of futures.
- `LocalVectorStoreDriver.persist_file` for persisting vectors and chunks in a text file.
- `Entry.to_artifact()` for easy vector store entry conversions into Griptape artifacts.
- `BaseVectorStoreDriver.does_entry_exist()` to check if an entry exists in the vector store.
- `GoogleWebSearchDriver` to web search with the Google Customsearch API.
- `DuckDuckGoWebSearchDriver` to web search with the DuckDuckGo search SDK.
- `ProxyWebScraperDriver` to web scrape using proxies.
- Parameter `session` on `AmazonBedrockStructureConfig`.
- Parameter `meta` on `TextArtifact`.
- `VectorStoreClient` improvements:
  - `VectorStoreClient.query_params` dict for custom query params.
  - `VectorStoreClient.process_query_output_fn` for custom query output processing logic.
- Parameter `fail_fast` to `Structure`.
- `BooleanArtifact` for handling boolean values.
- `typos` to dev dependencies to catch typos in code/docs.
- `Message` for storing messages in a `PromptStack`. Messages consist of a role, content, and usage.
- `DeltaMessage` for storing partial messages in a `PromptStack`. Multiple `DeltaMessage` can be combined to form a `Message`.
- `TextMessageContent` for storing textual content in a `Message`.
- `ImageMessageContent` for storing image content in a `Message`.
- Support for adding `TextArtifact`s, `ImageArtifact`s, and `ListArtifact`s to `PromptStack`.
- Support for image inputs to `OpenAiChatPromptDriver`, `AzureOpenAiChatPromptDriver`, `AmazonBedrockPromptDriver`, `AnthropicPromptDriver`, and `GooglePromptDriver`.
- Input/output token usage metrics to all Prompt Drivers. 
- `FinishPromptEvent.input_token_count` and `FinishPromptEvent.output_token_count`.
- Support for storing Artifacts as inputs/outputs in Conversation Memory Runs.
- `Agent.input` for passing Artifacts as input.
- Support for `PromptTask`s to take `TextArtifact`s, `ImageArtifact`s, and `ListArtifact`s as input.
- `JsonArtifact` for handling de/seralization of values.

### Changed
- **BREAKING**: Moved/renamed `griptape.utils.PromptStack` to `griptape.common.PromptStack`.
- **BREAKING**: Renamed `PromptStack.inputs` to `PromptStack.messages`.
- **BREAKING**: Moved `PromptStack.USER_ROLE`, `PromptStack.ASSISTANT_ROLE`, and `PromptStack.SYSTEM_ROLE` to `Message`.
- **BREAKING**: Updated return type of `PromptDriver.try_run` from `TextArtifact` to `Message`.
- **BREAKING**: Updated return type of `PromptDriver.try_stream` from `Iterator[TextArtifact]` to `Iterator[DeltaMessage]`.
- **BREAKING**: Removed `BasePromptEvent.token_count` in favor of `FinishPromptEvent.input_token_count` and `FinishPromptEvent.output_token_count`.
- **BREAKING**: Removed `StartPromptEvent.prompt`. Use `StartPromptEvent.prompt_stack` instead.
- **BREAKING**: Removed `Agent.input_template` in favor of `Agent.input`.
- **BREAKING**: `BasePromptDriver.run` now returns a `Message` instead of a `TextArtifact`. For compatibility, `Message.value` contains the Message's Artifact value
- **BREAKING**: `BaseVectorStoreDriver.upsert_text_artifact()` and `BaseVectorStoreDriver.upsert_text()` use artifact/string values to generate `vector_id` if it wasn't implicitly passed. This change ensures that we don't generate embeddings for the same content every time.
- **BREAKING**: Removed `VectorQueryEngine` in favor of `RagEngine`.
- **BREAKING**: Removed `TextQueryTask` in favor of `RagTask`.
- **BREAKING**: `TextArtifactStorage` now requires `vector_store_driver` and `rag_engine` in place of `vector_query_engine`.
- **BREAKING**: Moved `load_artifacts()` from `BaseQueryEngine` to `BaseVectorStoreDriver`.
- **BREAKING**: Merged `BaseVectorStoreDriver.QueryResult` into `BaseVectorStoreDriver.Entry`.
- **BREAKING**: Replaced `query_engine` with `vector_store_driver` in `VectorStoreClient`.
- **BREAKING**: removed parameters `google_api_lang`, `google_api_key`, `google_api_search_id`, `google_api_country` on `WebSearch` in favor of `web_search_driver`.
- **BREAKING**: removed `VectorStoreClient.top_n` and `VectorStoreClient.namespace` in favor of `VectorStoreClient.query_params`.
- **BREAKING**: All `futures_executor` fields renamed to `futures_executor_fn` and now accept callables instead of futures; wrapped all future `submit` calls with the `with` block to address future executor shutdown issues.
- `GriptapeCloudKnowledgeBaseClient` migrated to `/search` api.
- Default Prompt Driver model in `GoogleStructureConfig` to `gemini-1.5-pro`.

### Fixed
- `CoherePromptDriver` to properly handle empty history.
- `StructureVisualizer.to_url()` by wrapping task IDs in single quotes. 

## [0.27.2] - 2024-06-27

### Fixed
- Avoid adding duplicate Tokenizer stop sequences in a `ToolkitTask`.
- Fixed token count calculation in `VectorQueryEngine`.

## [0.27.1] - 2024-06-20

### Added
- Support for Claude 3.5 Sonnet in `AnthropicPromptDriver` and `AmazonBedrockPromptDriver`.

### Changed
- Base Tool schema so that `input` is optional when no Tool Activity schema is set.
- Tool Task system prompt for better results with lower-end models. 
- Default Prompt Driver model to Claude 3.5 Sonnet in `AnthropicStructureConfig` and `AmazonBedrockStructureConfig.`

## [0.27.0] - 2024-06-19

### Added
- `BaseTask.add_child()` to add a child task to a parent task.
- `BaseTask.add_children()` to add multiple child tasks to a parent task.
- `BaseTask.add_parent()` to add a parent task to a child task.
- `BaseTask.add_parents()` to add multiple parent tasks to a child task.
- `Structure.resolve_relationships()` to resolve asymmetrically defined parent/child relationships. In other words, if a parent declares a child, but the child does not declare the parent, the parent will automatically be added as a parent of the child when running this method. The method is invoked automatically by `Structure.before_run()`.
- `CohereEmbeddingDriver` for using Cohere's embeddings API.
- `CohereStructureConfig` for providing Structures with quick Cohere configuration.
- `AmazonSageMakerJumpstartPromptDriver.inference_component_name` for setting the `InferenceComponentName` parameter when invoking an endpoint.
- `AmazonSageMakerJumpstartEmbeddingDriver.inference_component_name` for setting the `InferenceComponentName` parameter when invoking an endpoint.
- `AmazonSageMakerJumpstartEmbeddingDriver.custom_attributes` for setting custom attributes when invoking an endpoint.
- `ToolkitTask.response_stop_sequence` for overriding the default Chain of Thought stop sequence.
- `griptape.utils.StructureVisualizer` for visualizing Workflow structures with Mermaid.js
- `BaseTask.parents_outputs` to get the textual output of all parent tasks. 
- `BaseTask.parents_output_text` to get a concatenated string of all parent tasks' outputs.
- `parents_output_text` to Workflow context.
- `OllamaPromptModelDriver` for using models with Ollama.
- Parameter `output` on `Structure` as a convenience for `output_task.output`

### Changed
- **BREAKING**: `Workflow` no longer modifies task relationships when adding tasks via `tasks` init param, `add_tasks()` or `add_task()`. Previously, adding a task would automatically add the previously added task as its parent. Existing code that relies on this behavior will need to be updated to explicitly add parent/child relationships using the API offered by `BaseTask`.
- **BREAKING**: Removed `AmazonBedrockPromptDriver.prompt_model_driver` as it is no longer needed with the `AmazonBedrockPromptDriver` Converse API implementation.
- **BREAKING**: Removed `BedrockClaudePromptModelDriver`.
- **BREAKING**: Removed `BedrockJurassicPromptModelDriver`.
- **BREAKING**: Removed `BedrockLlamaPromptModelDriver`.
- **BREAKING**: Removed `BedrockTitanPromptModelDriver`.
- **BREAKING**: Removed `BedrockClaudeTokenizer`, use `SimpleTokenizer` instead.
- **BREAKING**: Removed `BedrockJurassicTokenizer`, use `SimpleTokenizer` instead.
- **BREAKING**: Removed `BedrockLlamaTokenizer`, use `SimpleTokenizer` instead.
- **BREAKING**: Removed `BedrockTitanTokenizer`, use `SimpleTokenizer` instead.
- **BREAKING**: Removed `OpenAiChatCompletionPromptDriver` as it uses the legacy [OpenAi Completions API](https://platform.openai.com/docs/api-reference/completions).
- **BREAKING**: Removed `BasePromptDriver.count_tokens()`.
- **BREAKING**: Removed `BasePromptDriver.max_output_tokens()`.
- **BREAKING**: Moved/renamed `PromptStack.add_to_conversation_memory` to `BaseConversationMemory.add_to_prompt_stack`.
- **BREAKING**: Moved `griptape.constants.RESPONSE_STOP_SEQUENCE` to `ToolkitTask`.
- **BREAKING**: Renamed `AmazonSagemakerPromptDriver` to `AmazonSageMakerJumpstartPromptDriver`.
- **BREAKING**: Removed `SagemakerFalconPromptModelDriver`, use `AmazonSageMakerJumpstartPromptDriver` instead.
- **BREAKING**: Removed `SagemakerLlamaPromptModelDriver`, use `AmazonSageMakerJumpstartPromptDriver` instead.
- **BREAKING**: Renamed `AmazonSagemakerEmbeddingDriver` to `AmazonSageMakerJumpstartEmbeddingDriver`.
- **BREAKING**: Removed `SagemakerHuggingfaceEmbeddingModelDriver`, use `AmazonSageMakerJumpstartEmbeddingDriver` instead.
- **BREAKING**: Removed `SagemakerTensorflowHubEmbeddingModelDriver`, use `AmazonSageMakerJumpstartEmbeddingDriver` instead.
- **BREAKING**: `AmazonSageMakerJumpstartPromptDriver.model` parameter, which gets passed to `SageMakerRuntime.Client.invoke_endpoint` as `EndpointName`, is now renamed to `AmazonSageMakerPromptDriver.endpoint`.
- **BREAKING**: Removed parameter `template_generator` on `PromptSummaryEngine` and added parameters `system_template_generator` and `user_template_generator`.
- **BREAKING**: Removed template `engines/summary/prompt_summary.j2` and added templates `engines/summary/system.j2` and `engines/summary/user.j2`.
- `ToolkitTask.RESPONSE_STOP_SEQUENCE` is now only added when using `ToolkitTask`.
- Updated Prompt Drivers to use `BasePromptDriver.max_tokens` instead of using `BasePromptDriver.max_output_tokens()`.
- Improved error message when `GriptapeCloudKnowledgeBaseClient` does not have a description set.
- Updated `AmazonBedrockPromptDriver` to use [Converse API](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html).
- `Structure.before_run()` now automatically resolves asymmetrically defined parent/child relationships using the new `Structure.resolve_relationships()`.
- Updated `HuggingFaceHubPromptDriver` to use `transformers`'s `apply_chat_template`.
- Updated `HuggingFacePipelinePromptDriver` to use chat features of `transformers.TextGenerationPipeline`.
- Updated `CoherePromptDriver` to use Cohere's latest SDK.
- Moved Task reset logic for all Structures to `Structure.before_run`.
- Updated default prompt templates for `PromptSummaryEngine`.
- Updated template `templates/tasks/tool_task/system.j2`.

### Fixed
- `Workflow.insert_task()` no longer inserts duplicate tasks when given multiple parent tasks.
- Performance issue in `OpenAiChatPromptDriver` when extracting unused rate-limiting headers.
- Streaming not working when using deprecated `Structure.stream` field.
- Raw Tool output being lost when being executed by ActionsSubtask.
- Re-order Workflow tasks on every task execution wave.
- `Workflow.insert_task()` enumerates by parent id equality, opposed to object equality.
- Web Loader to catch Exceptions and properly return an ErrorArtifact.
- Conversation Memory entry only added if `output_task.output` is not `None` on all `Structures`
- `TextArtifacts` contained in `ListArtifact` returned by `WebSearch.search` to properly formatted stringified JSON.
- Structure run args not being set immediately.
- Input and output logging in BaseAudioInputTasks and BaseAudioGenerationTasks
- Validation of `max_tokens` < 0 on `BaseChunker`

## [0.26.0] - 2024-06-04

### Added
- `AzureOpenAiStructureConfig` for providing Structures with all Azure OpenAI Driver configuration.
- `AzureOpenAiVisionImageQueryDriver` to support queries on images using Azure's OpenAI Vision models.
- `AudioLoader` for loading audio content into an `AudioArtifact`.
- `AudioTranscriptionTask` and `AudioTranscriptionClient` for transcribing audio content in Structures.
- `OpenAiAudioTranscriptionDriver` for integration with OpenAI's speech-to-text models, including Whisper.
- Parameter `env` to `BaseStructureRunDriver` to set environment variables for a Structure Run.
- `PusherEventListenerDriver` to enable sending of framework events over a Pusher WebSocket.

### Changed
- **BREAKING**: Updated OpenAI-based image query drivers to remove Vision from the name.
- **BREAKING**: `off_prompt` now defaults to `False` on all Tools, making Task Memory something that must be explicitly opted into.
- **BREAKING**: Removed `StructureConfig.global_drivers`. Pass Drivers directly to the Structure Config instead. 
- **BREAKING**: Removed `StructureConfig.task_memory` in favor of configuring directly on the Structure.  
- **BREAKING**: Updated OpenAI-based image query drivers to remove Vision from the name.
- **BREAKING**: `off_prompt` now defaults to `False` on all Tools, making Task Memory something that must be explicitly opted into.
- **BREAKING**: `AmazonSageMakerPromptDriver.model` parameter, which gets passed to `SageMakerRuntime.Client.invoke_endpoint` as `EndpointName`, is now renamed to `AmazonSageMakerPromptDriver.endpoint`.
- **BREAKING**: `AmazonSageMakerPromptDriver.model` parameter is now optional being passed to `SageMakerRuntime.Client.invoke_endpoint` as `InferenceComponentName` (instead of `EndpointName`).
- **BREAKING**: `SageMakerLlamaPromptModelDriver` modified to exclusively support the Llama 3 Instruct model deployed via SageMaker JumpStart. (Support for Llama 2 models has been removed.)
- Simplified custom Task Memory configurations by making several `TextArtifactStorage` Engines optional.
- Default the value of `azure_deployment` on all Azure Drivers to the model the Driver is using.
- Field `azure_ad_token` on all Azure Drivers is no longer serializable.
- Default standard OpenAI and Azure OpenAI image query model to `gpt-4o`.
- Error message to be more helpful when importing optional dependencies.

### Fixed
- Extra fields being excluded when using `SerializableMixin.from_dict`.
- Validation of `max_tokens` < 0 on `BaseChunker`

## [0.25.1] - 2024-05-15

### Fixed
- Honor `namespace` in `RedisVectorStoreDriver.query()`.
- Correctly set the `meta`, `score`, and `vector` fields of query result returned from `RedisVectorStoreDriver.query()`.
- Standardize behavior between omitted and empty actions list when initializing `ActionsSubtask`.

### Added
- Optional event batching on Event Listener Drivers.
- `id` field to all events.

### Changed
- Default behavior of Event Listener Drivers to batch events.
- Default behavior of OpenAiStructureConfig to utilize `gpt-4o` for prompt_driver.

## [0.25.0] - 2024-05-06

### Added
- `list_files_from_disk` activity to `FileManager` Tool.
- Support for Drivers in `EventListener`.
- `AmazonSqsEventListenerDriver` for sending events to an Amazon SQS queue.
- `AwsIotCoreEventListenerDriver` for sending events to a topic on AWS IoT Core.
- `GriptapeCloudEventListenerDriver` for sending events to Griptape Cloud.
- `WebhookEventListenerDriver` for sending events to a webhook.
- `BaseFileManagerDriver` to abstract file management operations.
- `LocalFileManagerDriver` for managing files on the local file system.
- Optional `BaseLoader.encoding` field.
- `BlobLoader` for loading arbitrary binary data as a `BlobArtifact`.
- `model` field to `StartPromptEvent` and `FinishPromptEvent`.
- `input_task_input` and `input_task_output` fields to `StartStructureRunEvent`.
- `output_task_input` and `output_task_output` fields to `FinishStructureRunEvent`.
- `AmazonS3FileManagerDriver` for managing files on Amazon S3.
- `MediaArtifact` as a base class for `ImageArtifact` and future media Artifacts.
- Optional `exception` field to `ErrorArtifact`.
- `StructureRunClient` for running other Structures via a Tool.
- `StructureRunTask` for running Structures as a Task from within another Structure.
- `GriptapeCloudStructureRunDriver` for running Structures in Griptape Cloud.
- `LocalStructureRunDriver` for running Structures in the same run-time environment as the code that is running the Structure.

### Changed
- **BREAKING**: Secret fields (ex: api_key) removed from serialized Drivers.
- **BREAKING**: Remove `FileLoader`.
- **BREAKING**: `CsvLoader` no longer accepts `str` file paths as a source. It will now accept the content of the CSV file as a `str` or `bytes` object.
- **BREAKING**: `PdfLoader` no longer accepts `str` file content, `Path` file paths or `IO` objects as sources. Instead, it will only accept the content of the PDF file as a `bytes` object.
- **BREAKING**: `TextLoader` no longer accepts `Path` file paths as a source. It will now accept the content of the text file as a `str` or `bytes` object.
- **BREAKING**: `FileManager.default_loader` is now `None` by default.
- **BREAKING** Bumped `pinecone` from `^2` to `^3`.
- **BREAKING**: Removed `workdir`, `loaders`, `default_loader`, and `save_file_encoding` fields from `FileManager` and added `file_manager_driver`.
- **BREAKING**: Removed `mime_type` field from `ImageArtifact`. `mime_type` is now a property constructed using the Artifact type and `format` field.
- Improved RAG performance in `VectorQueryEngine`.
- Moved [Griptape Docs](https://github.com/griptape-ai/griptape-docs) to this repository.
- Updated `EventListener.handler`'s behavior so that the return value will be passed to the `EventListenerDriver.try_publish_event_payload`'s `event_payload` parameter.

### Fixed
- Type hint for parameter `azure_ad_token_provider` on Azure OpenAI drivers to `Optional[Callable[[], str]]`.
- Missing parameters `azure_ad_token` and `azure_ad_token_provider` on the default client for `AzureOpenAiCompletionPromptDriver`.

## [0.24.2] - 2024-04-04

- Fixed FileManager.load_files_from_disk schema.

## [0.24.1] - 2024-03-28

### Fixed 

- Fixed boto3 type-checking stub dependency.

### Changed

- Use `schema` instead of `jsonschema` for JSON validation.

## [0.24.0] - 2024-03-27

### Added
- Every subtask in `ToolkitTask` can now execute multiple actions in parallel.
- Added `BaseActionSubtaskEvent.subtask_actions`.
- Support for `text-embedding-3-small` and `text-embedding-3-large` models.
- `GooglePromptDriver` and `GoogleTokenizer` for use with `gemini-pro`. 
- `GoogleEmbeddingDriver` for use with `embedding-001`. 
- `GoogleStructureConfig` for providing Structures with Google Prompt and Embedding Driver configuration.
- Support for `claude-3-opus`, `claude-3-sonnet`, and `claude-3-haiku` in `AnthropicPromptDriver`.
- Support for `anthropic.claude-3-sonnet-20240229-v1:0` and `anthropic.claude-3-haiku-20240307-v1:0` in `BedrockClaudePromptModelDriver`.
- `top_k` and `top_p` parameters in `AnthropicPromptDriver`.
- Added `AnthropicImageQueryDriver` for Claude-3 multi-modal models
- Added `AmazonBedrockImageQueryDriver` along with `BedrockClaudeImageQueryDriverModel` for Claude-3 in Bedrock support
- `BaseWebScraperDriver` allowing multiple web scraping implementations.
- `TrafilaturaWebScraperDriver` for scraping text from web pages using trafilatura.
- `MarkdownifyWebScraperDriver` for scraping text from web pages using playwright and converting to markdown using markdownify.
- `VoyageAiEmbeddingDriver` for use with VoyageAi's embedding models. 
- `AnthropicStructureConfig` for providing Structures with Anthropic Prompt and VoyageAi Embedding Driver configuration.
- `QdrantVectorStoreDriver` to integrate with Qdrant vector databases.

### Fixed
- Improved system prompt in `ToolTask` to support more use cases.

### Changed
- **BREAKING**: `ActionSubtask` was renamed to `ActionsSubtask`.
- **BREAKING**: Removed `subtask_action_name`, `subtask_action_path`, and `subtask_action_input` in `BaseActionSubtaskEvent`.
- **BREAKING**: `OpenAiVisionImageQueryDriver` field `model` no longer defaults to `gpt-4-vision-preview` and must be specified
- Default model of `OpenAiEmbeddingDriver` to `text-embedding-3-small`.
- Default model of `OpenAiStructureConfig` to `text-embedding-3-small`.
- `BaseTextLoader` to accept a `BaseChunker`.
- Default model of `AmazonBedrockStructureConfig` to `anthropic.claude-3-sonnet-20240229-v1:0`.
- `AnthropicPromptDriver` and `BedrockClaudePromptModelDriver` to use Anthropic's Messages API.
- `OpenAiVisionImageQueryDriver` now has a required field `max_tokens` that defaults to 256

## [0.23.2] - 2024-03-15

### Fixed
- Deprecation warnings not displaying for `Structure.prompt_driver`, `Structure.embedding_driver`, and `Structure.stream`.
- `DummyException` error message not fully displaying.
- `StructureConfig.task_memory` not defaulting to using `StructureConfig.global_drivers` by default.

## [0.23.1] - 2024-03-07

### Fixed
- Action Subtask incorrectly raising an exception for actions without an input. 
- Incorrect `GriptapeCloudKnowledgeBaseClient`'s API URLs. 
- Issue with Tool Task system prompt causing the LLM to generate an invalid action.

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
- `BedrockStableDiffusionImageGenerationModelDriver` request parameters for SDXLv1 (`stability.stable-diffusion-xl-v1`).
- `BedrockStableDiffusionImageGenerationModelDriver` correctly handles the CONTENT_FILTERED response case.

### Changed
- **BREAKING**: Make `index_name` on `MongoDbAtlasVectorStoreDriver` a required field.
- **BREAKING**: Remove `create_index()` from `MarqoVectorStoreDriver`, `OpenSearchVectorStoreDriver`, `PineconeVectorStoreDriver`, `RedisVectorStoreDriver`.
- **BREAKING**: `ImageLoader().load()` now accepts image bytes instead of a file path.
- **BREAKING**: Request parameters for `BedrockStableDiffusionImageGenerationModelDriver` have been updated for `stability.stable-diffusion-xl-v1`. Use this over the now deprecated `stability.stable-diffusion-xl-v0`.
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
- `ToolkitTask`'s user subtask prompt occasionally causing a loop with Chain of Thought.

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
- `AmazonSageMakerJumpstartEmbeddingDriver` for using Amazon SageMaker to generate embeddings. Thanks @KaushikIyer16!
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
