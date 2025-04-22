# Changelog

All notable changes to this project will be documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.6.4](https://github.com/griptape-ai/griptape/compare/v1.6.3...v1.6.4) (2025-04-22)


### Bug Fixes

* **drivers-prompt-amazon-bedrock:** don't error when passing non-text ([fea3068](https://github.com/griptape-ai/griptape/commit/fea30687734071b7c461e097d144b1fa2c0e018c))
* **drivers-prompt-amazon-bedrock:** support reasoning content ([#1900](https://github.com/griptape-ai/griptape/issues/1900)) ([63ba1bb](https://github.com/griptape-ai/griptape/commit/63ba1bbeda6c127cb650984b314b22ee44a4668d)), closes [#1897](https://github.com/griptape-ai/griptape/issues/1897)
* **subtasks:** handle non-string inputs during schema validation subtask ([fea3068](https://github.com/griptape-ai/griptape/commit/fea30687734071b7c461e097d144b1fa2c0e018c))

## [1.6.3](https://github.com/griptape-ai/griptape/compare/v1.6.2...v1.6.3) (2025-04-21)


### Bug Fixes

* remove  from Message if  is an empty array ([9c066c3](https://github.com/griptape-ai/griptape/commit/9c066c3f572faa005f52ce1bda352207ba0cd9fc))
* remove `content` from Message if `content` is an empty array ([#1895](https://github.com/griptape-ai/griptape/issues/1895)) ([9c066c3](https://github.com/griptape-ai/griptape/commit/9c066c3f572faa005f52ce1bda352207ba0cd9fc))

## [1.6.2](https://github.com/griptape-ai/griptape/compare/v1.6.1...v1.6.2) (2025-04-17)


### Bug Fixes

* **deps:** pin marshmallow &lt;4 to avoid backwards incompatible changes ([#1891](https://github.com/griptape-ai/griptape/issues/1891)) ([cec5199](https://github.com/griptape-ai/griptape/commit/cec5199dc29758796a6fe28fd5d208cf6dd23fc5))

## [1.6.1](https://github.com/griptape-ai/griptape/compare/v1.6.0...v1.6.1) (2025-04-14)


### Bug Fixes

* implement pydantic model deserialization ([#1877](https://github.com/griptape-ai/griptape/issues/1877)) ([7345b49](https://github.com/griptape-ai/griptape/commit/7345b495febee1ac3b0d2b13048adbddc2c8156a))

## [1.6.0](https://github.com/griptape-ai/griptape/compare/v1.5.0...v1.6.0) (2025-04-08)


### ✨ Features

* add output schema validation subtask ([#1865](https://github.com/griptape-ai/griptape/issues/1865)) ([0c68e8f](https://github.com/griptape-ai/griptape/commit/0c68e8f7a2960ca8214d95c6445e590db70b37af))
* **drivers:** Add GriptapeCloudImageGenerationDriver ([#1862](https://github.com/griptape-ai/griptape/issues/1862)) ([a589028](https://github.com/griptape-ai/griptape/commit/a589028ae90d4bce9988b6ccfe4bd2de4a012c65))
* parameterize event types on Stream util ([#1863](https://github.com/griptape-ai/griptape/issues/1863)) ([260269d](https://github.com/griptape-ai/griptape/commit/260269d340da538372e798c8fa1ae9f79df9b2e4))


### 🐛 Bug Fixes

* demote tokenizer log from warning to debug ([#1845](https://github.com/griptape-ai/griptape/issues/1845)) ([fc27554](https://github.com/griptape-ai/griptape/commit/fc27554baae436cc2bfbb476b8c99bb651c7c6cc))
* **deps:** bump minimum attrs version to one with attrs.NothingType ([#1855](https://github.com/griptape-ai/griptape/issues/1855)) ([6e06214](https://github.com/griptape-ai/griptape/commit/6e062148e4a28ed7026b3b33ded4a6b6a4229e4f))
* **serialization:** add fallback JSON encoder for SerializableMixin ([#1870](https://github.com/griptape-ai/griptape/issues/1870)) ([c43134d](https://github.com/griptape-ai/griptape/commit/c43134d6c91f1e7ec10887635f05bcb1753c2b10))
* **tokenizers-simple:** set model to None to avoid serialization issues ([#1867](https://github.com/griptape-ai/griptape/issues/1867)) ([050d949](https://github.com/griptape-ai/griptape/commit/050d949ef423287f52c3307b18bc41703a8af953))


### 📚 Documentation

* add docs on openai's reasoning models ([#1843](https://github.com/griptape-ai/griptape/issues/1843)) ([a4e91e1](https://github.com/griptape-ai/griptape/commit/a4e91e1faef67a91f6ce23a24d814774a5dea7f7)), closes [#1688](https://github.com/griptape-ai/griptape/issues/1688)
* add info on Libraries and the Hybrid Knowledge Base types ([022ac77](https://github.com/griptape-ai/griptape/commit/022ac77dddd138bd57ca7d38938fef1f357727e9))
* add link back to optional dependencies ([#1871](https://github.com/griptape-ai/griptape/issues/1871)) ([bc19553](https://github.com/griptape-ai/griptape/commit/bc1955301a8fb4cf3b3ea62073a7ecbd13f861c1))
* fix duplicated word typo ([#1861](https://github.com/griptape-ai/griptape/issues/1861)) ([718d2a3](https://github.com/griptape-ai/griptape/commit/718d2a3553652764c88d451f3f7a53649803d0ba))
* remove duplicate log output ([#1841](https://github.com/griptape-ai/griptape/issues/1841)) ([da9f9de](https://github.com/griptape-ai/griptape/commit/da9f9dea05df4782f798422bff7f2d001486130f))

## [1.5.0](https://github.com/griptape-ai/griptape/compare/v1.4.0...v1.5.0) (2025-03-13)


### ✨ Features

* **configs-drivers-gemini:** update default embedding driver model to ([9ba2496](https://github.com/griptape-ai/griptape/commit/9ba249658f1f087739ff1d8b37852f790f676d3e))
* **configs-drivers-gemini:** update default prompt driver model to `gemini-2.0-flash` ([9ba2496](https://github.com/griptape-ai/griptape/commit/9ba249658f1f087739ff1d8b37852f790f676d3e))
* **drivers-embedding-titan:** add support for generating image embeddings ([1841f0f](https://github.com/griptape-ai/griptape/commit/1841f0f8e36dc3500400a69e8e1dff8bc63e0345))
* **drivers-embedding-voyageai:** add support for generating image embeddings ([1841f0f](https://github.com/griptape-ai/griptape/commit/1841f0f8e36dc3500400a69e8e1dff8bc63e0345))
* **drivers-embedding:** add support for embedding ImageArtifacts ([1841f0f](https://github.com/griptape-ai/griptape/commit/1841f0f8e36dc3500400a69e8e1dff8bc63e0345))
* **drivers-local-vector:** support persisting multi-modal entries ([1841f0f](https://github.com/griptape-ai/griptape/commit/1841f0f8e36dc3500400a69e8e1dff8bc63e0345))
* **drivers-vector:** support upserting/querying with ImageArtifacts ([1841f0f](https://github.com/griptape-ai/griptape/commit/1841f0f8e36dc3500400a69e8e1dff8bc63e0345))
* **drivers:** add PerplexityPromptDriver and PerplexityWebSearchDriver ([#1755](https://github.com/griptape-ai/griptape/issues/1755)) ([7163bf3](https://github.com/griptape-ai/griptape/commit/7163bf3402bcf5da1045b36e05ec1ee0b3bd357b))
* **drivers:** update default models to latest for Anthropic/Bedrock Driver Configs ([b3e4b68](https://github.com/griptape-ai/griptape/commit/b3e4b6817528536dd81b0a847f45c7296212d1b1))
* **serialization:** add `serializable_overrides` and `types_overrides` parameters to `to_dict/json` and `from_dict/json` methods ([c383ba6](https://github.com/griptape-ai/griptape/commit/c383ba6e26531eea65c99d9e85a29978eb0ba133))
* **tasks-prompt:** add `reflect_on_tool_use` flag to disable LLM reflection ([#1810](https://github.com/griptape-ai/griptape/issues/1810)) ([ecb665d](https://github.com/griptape-ai/griptape/commit/ecb665d067e74b82cd4cc0cebcb3c8b4734cec1b))


### 🐛 Bug Fixes

* **chunker:** correctly determine chunk midpoint when empty chunks are present ([#1800](https://github.com/griptape-ai/griptape/issues/1800)) ([8ec2a8a](https://github.com/griptape-ai/griptape/commit/8ec2a8a38b2bfb03a6e75c0396a7cd40b278e1c4))
* **decorators:** preserve type hints on `[@observable](https://github.com/observable)` decorator ([#1767](https://github.com/griptape-ai/griptape/issues/1767)) ([0e5a15c](https://github.com/griptape-ai/griptape/commit/0e5a15c7645db65a928aa5fb25d8be35bd8c9fba))
* **drivers-prompt-openai:** convert to text rather than error when passing GenericArtifacts ([#1830](https://github.com/griptape-ai/griptape/issues/1830)) ([fb3f2c4](https://github.com/griptape-ai/griptape/commit/fb3f2c46a0ef32b04da9d2b92a1b99af719da77f))
* **drivers-prompt-openai:** remove modalities default ([#1774](https://github.com/griptape-ai/griptape/issues/1774)) ([7e061b5](https://github.com/griptape-ai/griptape/commit/7e061b56963a9fe31a06c1eae4e62fe0094dc3a1))
* **drivers-vector-marqo:** fix upsert failing due to inability to upsert_vectors ([#1803](https://github.com/griptape-ai/griptape/issues/1803)) ([9b6bfff](https://github.com/griptape-ai/griptape/commit/9b6bfffaa8640ba7277c287be4fa0a125b94d772))
* **drivers-vector:** don't mutate same instance of meta ([#1782](https://github.com/griptape-ai/griptape/issues/1782)) ([dd138ca](https://github.com/griptape-ai/griptape/commit/dd138caea9dabd74c515592c697415d645fdca4d))
* **serialization:** support serializing more Driver types ([c383ba6](https://github.com/griptape-ai/griptape/commit/c383ba6e26531eea65c99d9e85a29978eb0ba133))


### 📦 Dependencies

* relax dependencies by removing upper bound constraint ([5171332](https://github.com/griptape-ai/griptape/commit/5171332bf7217841eea44d84133fb00ecee6322a))


### 📚 Documentation

* add light/dark mode toggle ([ff3d2b6](https://github.com/griptape-ai/griptape/commit/ff3d2b620e20dbf8224e303ccbf5eafd02723869))
* add log output to every example that produces it ([0407fc7](https://github.com/griptape-ai/griptape/commit/0407fc747c177ce6e31c58058d590e23f02c81ac))
* categorize driver nav links ([ff3d2b6](https://github.com/griptape-ai/griptape/commit/ff3d2b620e20dbf8224e303ccbf5eafd02723869))
* **custom-tools:** improve docs for creating custom tools ([#1791](https://github.com/griptape-ai/griptape/issues/1791)) ([25b1276](https://github.com/griptape-ai/griptape/commit/25b12769ba75f5e806b834e25570e3c698d53389))
* **engines:** improve documentation on Rag Engines. ([bdc1921](https://github.com/griptape-ai/griptape/commit/bdc19214501a80006d5ff44ff4c90707c04086b1))
* improve docs landing page ([ff3d2b6](https://github.com/griptape-ai/griptape/commit/ff3d2b620e20dbf8224e303ccbf5eafd02723869))
* improve framework overview ([ff3d2b6](https://github.com/griptape-ai/griptape/commit/ff3d2b620e20dbf8224e303ccbf5eafd02723869))
* improve overview page ([#1832](https://github.com/griptape-ai/griptape/issues/1832)) ([ff3d2b6](https://github.com/griptape-ai/griptape/commit/ff3d2b620e20dbf8224e303ccbf5eafd02723869))
* improve README ([ff3d2b6](https://github.com/griptape-ai/griptape/commit/ff3d2b620e20dbf8224e303ccbf5eafd02723869))
* move recipes into framework section ([ff3d2b6](https://github.com/griptape-ai/griptape/commit/ff3d2b620e20dbf8224e303ccbf5eafd02723869))
* move recipes into framework section ([ff3d2b6](https://github.com/griptape-ai/griptape/commit/ff3d2b620e20dbf8224e303ccbf5eafd02723869))
* **recipes:** add example of talking to audio file ([#1794](https://github.com/griptape-ai/griptape/issues/1794)) ([fe27585](https://github.com/griptape-ai/griptape/commit/fe27585cf81dea16127f43840a76b7b5b74af3c9))
* rename examples to recipes ([ff3d2b6](https://github.com/griptape-ai/griptape/commit/ff3d2b620e20dbf8224e303ccbf5eafd02723869))
* **serialization:** add dedication page on serialization ([c383ba6](https://github.com/griptape-ai/griptape/commit/c383ba6e26531eea65c99d9e85a29978eb0ba133))
* simplify docs landing page ([ff3d2b6](https://github.com/griptape-ai/griptape/commit/ff3d2b620e20dbf8224e303ccbf5eafd02723869))
* update contributing guide ([ff3d2b6](https://github.com/griptape-ai/griptape/commit/ff3d2b620e20dbf8224e303ccbf5eafd02723869))

## [1.4.0](https://github.com/griptape-ai/griptape/compare/v1.3.0...v1.4.0) (2025-02-24)


### Features

* **drivers:** add GriptapeCloudPromptDriver ([#1692](https://github.com/griptape-ai/griptape/issues/1692)) ([7af49da](https://github.com/griptape-ai/griptape/commit/7af49daee247e72c60f3004d1d6b174942b20f57))
* **drivers:** add GrokPromptDriver ([f281702](https://github.com/griptape-ai/griptape/commit/f281702480b1081d25c4f87aa59421523deb75c2))
* **drivers:** use cloud server events for GriptapeCloudStructureRunDriver and GriptapeCloudAssistantDriver ([#1684](https://github.com/griptape-ai/griptape/issues/1684)) ([f0fef4c](https://github.com/griptape-ai/griptape/commit/f0fef4c54bc2692b7f422f76b40449e938528850))
* **tasks:** accept args in `BaseTask.run()` ([#1598](https://github.com/griptape-ai/griptape/issues/1598)) ([89c32d4](https://github.com/griptape-ai/griptape/commit/89c32d4530f4b2b4ef130180466393058cee628c))
* **tools:** allow setting allowlist and denylist on Tools ([#1743](https://github.com/griptape-ai/griptape/issues/1743)) ([4ee4515](https://github.com/griptape-ai/griptape/commit/4ee451598ca9b9475b948cfb0c57bcace27f6ab4))


### Bug Fixes

* **drivers-event-listener-griptape-cloud:** add type/timestamp fallbacks for custom events ([#1758](https://github.com/griptape-ai/griptape/issues/1758)) ([ef52194](https://github.com/griptape-ai/griptape/commit/ef52194138e3221c64e826f5664792c27596dc8f))
* **drivers-files-griptape-cloud:** pass correct parameters when listing files ([#1674](https://github.com/griptape-ai/griptape/issues/1674)) ([4b2f618](https://github.com/griptape-ai/griptape/commit/4b2f618616b1f1ba2110d6a27c2f6b486eb9d7cf))
* **drivers-prompt-azure-openai:** fix AzureOpenAiChatPromptDriver by removing unsupported "modalities" ([#1694](https://github.com/griptape-ai/griptape/issues/1694)) ([6699a3d](https://github.com/griptape-ai/griptape/commit/6699a3d5f91b63904b1134081c9148466faf7a14))
* **drivers-prompt-openai:** check existence of "audio" attribute ([23ca1c5](https://github.com/griptape-ai/griptape/commit/23ca1c5cc596894a4072afbb22f6f2b955cab759))
* **drivers-prompt-openai:** conditionally add modalities/reasoning_effort based on model ([#1668](https://github.com/griptape-ai/griptape/issues/1668)) ([b9311c1](https://github.com/griptape-ai/griptape/commit/b9311c114588d80229ad4b17f6539c9a2222cea7))
* **drivers:** lower max_attempts in ExponentialBackoffMixin to reasonable value ([#1725](https://github.com/griptape-ai/griptape/issues/1725)) ([29e4575](https://github.com/griptape-ai/griptape/commit/29e4575cd39adf3e6793a80ddf3d21caedc39def))
* **engines-eval:** fix evaluation parameters not being included in prompt ([#1751](https://github.com/griptape-ai/griptape/issues/1751)) ([762958f](https://github.com/griptape-ai/griptape/commit/762958f0da4ac4284dcac48b725b0e682aa081cf))
* properly serialize pydantic models ([#1757](https://github.com/griptape-ai/griptape/issues/1757)) ([ef83084](https://github.com/griptape-ai/griptape/commit/ef830842a531811e51f5e9e1643d41eb1531ad9a))
* **schema:** declare all artifacts for deserialization ([#1698](https://github.com/griptape-ai/griptape/issues/1698)) ([4904309](https://github.com/griptape-ai/griptape/commit/49043097980b4c30c5c378f71db40b11edd1623c))
* **tasks:** fix task input being lost on multiple Structure runs ([#1732](https://github.com/griptape-ai/griptape/issues/1732)) ([f9ac289](https://github.com/griptape-ai/griptape/commit/f9ac289715eeb24cb15cbb31e8e32c0e9fb00d45))
* **tasks:** remove deprecation warning on CodeExecutionTask.input ([#1709](https://github.com/griptape-ai/griptape/issues/1709)) ([0427296](https://github.com/griptape-ai/griptape/commit/04272965fdd6e332afba6c1f91695168bb72edc0))
* **utils:** wrap primitives with more specific artifact types ([#1676](https://github.com/griptape-ai/griptape/issues/1676)) ([91800ad](https://github.com/griptape-ai/griptape/commit/91800ad60b36c5bdf6a0c258df161ee5daee114f))


### Documentation

* **assistants:** add section to cloud docs, update nav, add docs pages for what is, getting started, and runs ([#1686](https://github.com/griptape-ai/griptape/issues/1686)) ([4f6f8ce](https://github.com/griptape-ai/griptape/commit/4f6f8cefe75c460ae691b230a14aab885eb0af6b))
* fix integration test examples ([#1724](https://github.com/griptape-ai/griptape/issues/1724)) ([4fe4558](https://github.com/griptape-ai/griptape/commit/4fe45586b0c3ab83b878e5aa4bfde28637adcdd6))
* **tasks:** improve CodeExecutionTask example ([#1710](https://github.com/griptape-ai/griptape/issues/1710)) ([8c61d91](https://github.com/griptape-ai/griptape/commit/8c61d91a53d49444e4e1ac355f5804d5455d80c9))
* **tools:** move tools to framework portion of docs ([#1713](https://github.com/griptape-ai/griptape/issues/1713)) ([c2b23bb](https://github.com/griptape-ai/griptape/commit/c2b23bbd3847de325bac96f7e22a339dfb97fa1b))

## [1.3.0] - 2025-02-07

### Added

- Provider-specific Driver namespaces (e.g., `griptape.drivers.prompt.openai`, `griptape.drivers.embedding.cohere`).
- Tool streaming support to `OllamaPromptDriver`.
- `DateTimeTool.add_timedelta` and `DateTimeTool.get_datetime_diff` for basic datetime arithmetic.
- Support for `pydantic.BaseModel`s anywhere `schema.Schema` is supported.
- Support for new serialization metadata, `serialization_key` and `deserialization_key` for more granular control over serialization. 
- Support for OpenAi reasoning models, `o1` and `o3`.
- Support for enums in `GriptapeCloudToolTool`.
- `LocalRerankDriver` for reranking locally.
- `griptape.utils.griptape_cloud.GriptapeCloudStructure` for automatically configuring Cloud-specific Drivers when in the Griptape Cloud Structures Runtime.
- Support for `AudioArtifact` inputs/outputs in `OpenAiChatPromptDriver`.

### Changed

- Added `DateTime.get_relative_datetime` to `DateTimeTool.denylist`. May be removed in a future release.
- Changed log level of `ActionsSubtask` errors from `EXCEPTION` to `DEBUG`.
- `GriptapeCloudStructureRunDriver` now publishes its events to the global event bus.
- Changed log level of Tool execution errors from `EXCEPTION` to `DEBUG`
- Improved mime type detection in `FileManagerTool`.
- Improve `SqlDriver.get_table_schema` speed.
- Cache `SqlDriver.get_table_schema` results.
- Updated Azure Drivers to use the latest Azure OpenAI API version, `2024-10-21`.

### Deprecated

- `griptape.drivers` namespace. Use provider-specific namespaces instead.

### Fixed

- Error when serializing `RagContext`.
- `Answer:` being trimmed from LLM's final answer even when using native tool calling. 
- `NotADirectoryError` being raised for valid list operations in `FileManagerTool`.
- `GriptapeCloudFileManagerDriver` list operation using wrong method when listing assets in a bucket.
- `GriptapeCloudAssistantDriver` not initializing `thread_id` when providing a `thread_alias` and `auto_create_thread=True`.
- Default Rulesets being duplicated when serializing `PromptTask`.
- Structured output with `tool` strategy not working with certain OpenAI-compatible Prompt Drivers during streaming.
- `Stream` cutting off early when running multiple Structures.


## [1.2.0] - 2025-01-21

### Added

- `BaseVectorStoreDriver.query_vector` for querying vector stores with vectors.
- Structured Output support for all Prompt Drivers.
- `PromptTask.output_schema` for setting an output schema to be used with Structured Output.
- `Agent.output_schema` for setting an output schema to be used on the Agent's Prompt Task.
- `BasePromptDriver.structured_output_strategy` for changing the Structured Output strategy between `native`, `tool`, and `rule`.
- Better type support to all Tasks.

### Changed
- Task bitshift operators can now take a list of Tasks.
- `GriptapeCloudAssistantDriver` and `OpenAiAssistantDriver` now automatically create a new Thread if one is not provided. Can be disabled with `auto_create_thread=False`.
- `GriptapeCloudAssistantDriver` and `OpenAiAssistantDriver` now return metadata (`thread_id`) on the response Artifact.
- `GriptapeCloudAssistantDriver` now accepts a `thread_alias` parameter for fetching a Thread by alias, creating one if it doesn't exist.
- `EvalEngine` to use structured output when generating evaluation steps.
- `GriptapeCloudVectorStoreDriver.query()` updated to non-deprecated Griptape Cloud API shape.

### Fixed

- Occasional crash during `FuturesExecutorMixin` cleanup.
- `BaseChunker` chunking more than necessary.
- `BaseLoader.reference` not being set when using `BaseLoader.parse` directly.
- `LocalVectorStoreDriver` returned Entries not containing the namespace.
- References being lost on Artifacts during chunking.
- `FootnotePromptResponseRagModule`'s system prompt causing it to not answer even with relevant chunks. 
- Chunker occasionally dropping suffix chunk separators.
- `PromptTask.conversation_memory` not working when set without a Structure.
- `GriptapeCloudAssistantDriver` overriding Rulesets and Knowledge Bases on Cloud.
- Missing `structure_ids` and `tool_ids` fields in `GriptapeCloudAssistantDriver`.

### Deprecated

- `FuturesExecutorMixin.futures_executor`. Use `FuturesExecutorMixin.create_futures_executor` instead.

## [1.1.1] - 2025-01-03

### Fixed

- Incorrect deprecation warning on `ToolkitTask`.

## [1.1.0] - 2024-12-31

### Added

- `PromptTask.conversation_memory` for setting the Conversation Memory on a Prompt Task.
- `Structure.conversation_memory_strategy` for setting whether Conversation Memory Runs should be created on a per-Structure or per-Task basis. Default is `per_structure`.
- `Structure.conversation_memory_strategy` for setting whether Conversation Memory Runs should be created on a per-Structure or per-Task basis. Default is `Structure.ConversationMemoryStrategy.PER_STRUCTURE`.
- `BranchTask` for selecting which Tasks (if any) to run based on a condition.
- Support for `BranchTask` in `StructureVisualizer`.
- `EvalEngine` for evaluating the performance of an LLM's output against a given input.
- `BaseFileLoader.save()` method for saving an Artifact to a destination.
- `Structure.run_stream()` for streaming Events from a Structure as an iterator.
- Support for `GenericMessageContent` in `AnthropicPromptDriver` and `AmazonBedrockPromptDriver`.
- Validators to `Agent` initialization.

### Changed

- Rulesets can now be serialized and deserialized.
- `ToolkitTask` now serializes its `tools` field.
- `PromptTask.prompt_driver` is now serialized.
- `PromptTask` can now do everything a `ToolkitTask` can do.
- Loosten `numpy`s version constraint to `>=1.26.4,<3`.

### Fixed

- Exception when calling `Structure.to_json()` after it has run.
- `Agent` unintentionally modifying `stream` for all Prompt Drivers.
- `StructureVisualizer.base_url` for setting the base URL on the url generated by `StructureVisualizer.to_url()`.
- `StructureVisualizer.query_params` for setting query parameters on the url generated by `StructureVisualizer.to_url()`.
- Parsing `ActionCallDeltaMessageContent`s with empty string `partial_input`s.
- `Stream` util not properly propagating thread contextvars.
- `ValueError` with `DuckDuckGoWebSearchDriver`.
- `Agent.stream` overriding `Agent.prompt_driver.stream` even when `Agent.prompt_driver` is explicitly provided.

### Deprecated

- `ToolkitTask`. `PromptTask` is a drop-in replacement.

## [1.0.0] - 2024-12-09

### Added

- `TrafilaturaWebScraperDriver.no_ssl` parameter to disable SSL verification. Defaults to `False`.
- `CsvExtractionEngine.format_header` parameter to format the header row.
- `PromptStack.from_artifact` factory method for creating a Prompt Stack with a user message from an Artifact.
- `OpenAiChatPromptDriver.parallel_tool_calls` parameter for toggling parallel tool calling. Defaults to `True`.
- `AssistantTask` for running Assistants in Structures.
- `GriptapeCloudAssistantDriver` for interacting with Griptape Cloud's Assistant API.
- `OpenAiAssistantDriver` for interacting with OpenAI's Assistant API.
- `GriptapeCloudToolTool` for running Griptape Cloud hosted Tools.
- `JsonLoader` for loading and parsing JSON files.
- `StructureVisualizer.build_node_id` field for customizing the node ID.
- Support for Python `3.13`.

### Changed

- **BREAKING**: Removed `stringcase` and `docker` from core dependencies. `ComputerTool` will now install these on the fly.
- **BREAKING**: Renamed `BaseTask.State.EXECUTING` to `BaseTask.State.RUNNING`.
- **BREAKING**: Renamed `BaseTask.is_executing()` to `BaseTask.is_running()`.
- **BREAKING**: Renamed `Structure.is_executing()` to `Structure.is_running()`.
- **BREAKING**: Removed ability to pass bytes to `BaseFileLoader.fetch`.
- **BREAKING**: Updated `CsvExtractionEngine.format_row` to format rows as comma-separated values instead of newline-separated key-value pairs.
- **BREAKING**: Removed all `ImageQueryDriver`s, use `PromptDriver`s instead.
- **BREAKING**: Removed `ImageQueryTask`, use `PromptTask` instead.
- **BREAKING**: Updated `ImageQueryTool.image_query_driver` to `ImageQueryTool.prompt_driver`.
- **BREAKING**: Updated `numpy` to `~2.0.2` and `pandas` to `^2.2`.
- **BREAKING**: Renamed `StructureRunTask.driver` to `StructureRunTask.structure_run_driver`.
- **BREAKING**: Renamed `StructureRunTool.driver` to `StructureRunTool.structure_run_driver`.
- **BREAKING**: Moved the following Google Tools to the [Griptape Google Extension](https://github.com/griptape-ai/griptape-google):
  - `GoogleCalendarTool`
  - `GoogleDocsTool`
  - `GoogleDriveTool`
  - `GoogleGmailTool`
- **BREAKING**: Moved the following AWS Tools to the [Griptape AWS Extension](https://github.com/griptape-ai/griptape-aws):
  - `AwsCliTool`
  - `AwsIamTool`
  - `AwsPricingTool`
  - `AwsS3Tool`
- **BREAKING**: Moved the `OpenWeatherTool` to the [Griptape Open Weather Extension](https://github.com/griptape-ai/griptape-open-weather)
- **BREAKING**: Removed `GriptapeCloudKnowledgeBaseTool`. Use a RAG Engine with `GriptapeCloudVectorStoreDriver` instead.
- **BREAKING**: Removed redundant Engines, use their respective Drivers instead.
  - Removed `ImageQueryEngine`, use `ImageQueryDriver`s instead.
  - Removed `InpaintingImageGenerationEngine`, use `ImageGenerationDriver`s instead.
  - Removed `OutpaintingImageGenerationEngine`, use `ImageGenerationDriver`s instead.
  - Removed `VariationImageGenerationEngine`, use `ImageGenerationDriver`s instead.
  - Removed `PromptImageGenerationEngine`, use `ImageGenerationDriver`s instead.
  - Removed `ImageGenerationEngine`, use `ImageGenerationDriver`s instead.
  - Removed `AudioTranscriptionEngine`, use `AudioTranscriptionDriver`s instead.
  - Removed `TextToSpeechEngine`, use `TextToSpeechDriver`s instead.
- **BREAKING**: Tools that previously took Engines now take their respective Drivers.
  - Updated `AudioTranscriptionTool.engine` to `AudioTranscriptionTool.audio_transcription_driver`.
  - Updated `TextToSpeechTool.engine` to `TextToSpeechTool.text_to_speech_driver`.
  - Updated `ImageQueryTool.image_query_engine` to `ImageQueryTool.image_query_driver`.
  - Updated `InpaintingImageGenerationTool.engine` to `InpaintingImageGenerationTool.image_generation_driver`.
  - Updated `OutpaintingImageGenerationTool.engine` to `OutpaintingImageGenerationTool.image_generation_driver`.
  - Updated `VariationImageGenerationTool.engine` to `VariationImageGenerationTool.image_generation_driver`.
  - Updated `PromptImageGenerationTool.engine` to `PromptImageGenerationTool.image_generation_driver`.
- **BREAKING**: Tasks that previously took Engines now take their respective Drivers.
  - Updated `AudioTranscriptionTask.audio_transcription_engine` to `AudioTranscriptionTask.audio_transcription_driver`.
  - Updated `TextToSpeechTask.text_to_speech_engine` to `TextToSpeechTask.text_to_speech_driver`.
  - Updated `ImageQueryTask.image_query_engine` to `ImageQueryTask.image_query_driver`.
  - Updated `InpaintingImageGenerationTask.image_query_engine` to `InpaintingImageGenerationTask.image_generation_driver`.
  - Updated `OutpaintingImageGenerationTask.image_query_engine` to `OutpaintingImageGenerationTask.image_generation_driver`.
  - Updated `VariationImageGenerationTask.image_query_engine` to `VariationImageGenerationTask.image_generation_driver`.
  - Updated `PromptImageGenerationTask.image_query_engine` to `PromptImageGenerationTask.image_generation_driver`.
- **BREAKING**: Renamed`BaseImageGenerationTask.all_negative_rulesets` to `BaseImageGenerationTask.negative_rulesets`.
- File Manager Driver path logic has been improved.
  - `LocalFileManagerDriver.workdir` can now be a relative path or absolute path. Relative paths will be prefixed with the current working directory.
  - `AmazonS3FileManagerDriver.workdir` can now be a relative path or absolute path. Relative paths will be prefixed with `/`.
  - `GriptapeCloudFileManagerDriver.workdir` can now be a relative path or absolute path. Relative paths will be prefixed with `/`.
  - Paths passed to `LocalFileManagerDriver` can now be relative or absolute. Absolute paths will be used as-is.
- `BasePromptDriver.run` can now accept an Artifact in addition to a Prompt Stack.
- Improved `CsvExtractionEngine` prompts.
- Tweaked `PromptResponseRagModule` system prompt to yield answers more consistently.
- Removed `azure-core` and `azure-storage-blob` dependencies.
- `GriptapeCloudFileManagerDriver` no longer requires `drivers-file-manager-griptape-cloud` extra.
- `TrafilaturaWebScraperDriver` no longer sets `no_ssl` to `True` by default.
- `AmazonBedrockPromptDriver` not working without setting `max_tokens`.
- `BaseImageGenerationTask` no longer prevents setting `negative_rulesets` _and_ `negative_rules` at the same time.
- `StructureVisualizer` now renders `StructureRunTask`s with a `LocalStructureRunDriver`.
- `StructureVisualizer` to titlecase the node IDs to avoid Mermaid.js reserved keywords.
- Updated Tokenizer model-to-max tokens lookup logic for more flexible matching.
- `BaseTool` now logs Tool activity exceptions after catching them.
- `BaseTool` now deep copies activity params.

### Fixed

- Use of deprecated `pkg_resources` in `BaseTool`.
- Error when serializing `JsonArtifact`s.
- `GriptapeCloudVectorStoreDriver` not pulling `api_key` from `GT_CLOUD_API_KEY` environment variable.
- `MarqoVectorStoreDriver.query` failing when `include_metadata` is `True`.
- `with_contextvars` not properly wrapping functions in some cases.
- Crash when calling `ToolkitTask.run()` directly.
- `@activity` decorator overwriting injected kwargs with default values as `None`.
- Multiple calls to `RuleMixin.rulesets` resulting in duplicate Rulesets.
- `BaseTool` incorrectly checking for empty values.

## [0.34.3] - 2024-11-13

### Fixed

- `ActionsSubtask.before_run` and `ActionsSubtask.after_run` being called twice in `ToolkitTask` and `Tooltask`.

## [0.34.2] - 2024-11-07

### Fixed

- Restore human-friendly default `ImageArtifact` and `AudioArtifact` names with file type extension.

## [0.34.1] - 2024-11-05

### Added

- `WebScraperTool.text_chunker` default value for `max_tokens`.

### Fixed

- `WebScraperTool` not using `text_chunker` override.
- Breaking change in `Chat.handle_output` behavior.

## [0.34.0] - 2024-10-29

### Added

- `griptape.configs.logging.JsonFormatter` for formatting logs as JSON.
- Request/response debug logging to all Prompt Drivers.
- `griptape.schemas.UnionField` for serializing union fields.
- `BaseEventListener.flush_events()` to flush events from an Event Listener.
- Exponential backoff to `BaseEventListenerDriver` for retrying failed event publishing.
- `BaseTask.task_outputs` to get a dictionary of all task outputs. This has been added to `Workflow.context` and `Pipeline.context`.
- `Chat.input_fn` for customizing the input to the Chat utility.
- `GriptapeCloudFileManagerDriver` for managing files on Griptape Cloud.
- `BaseFileManagerDriver.load_artifact()` & `BaseFileManagerDriver.save_artifact()` for loading & saving artifacts as files.
- Events `BaseChunkEvent`, `TextChunkEvent`, `ActionChunkEvent`.
- `wrapt` dependency for more robust decorators.
- `BasePromptDriver.extra_params` for passing extra parameters not explicitly declared by the Driver.
- `RunnableMixin` which adds `on_before_run` and `on_after_run` hooks.
- `griptape.utils.with_contextvars` utility for running functions with the current `contextvars` context.

### Changed

- **BREAKING**: Removed `BaseEventListenerDriver.publish_event` `flush` argument. Use `BaseEventListenerDriver.flush_events()` instead.
- **BREAKING**: Renamed parameter `driver` on `EventListener` to `event_listener_driver`.
- **BREAKING**: Updated `EventListener.handler` return value behavior.
  - If `EventListener.handler` returns `None`, the event will not be published to the `event_listener_driver`.
  - If `EventListener.handler` is None, the event will be published to the `event_listener_driver` as-is.
- **BREAKING**: Removed `CompletionChunkEvent`.
- **BREAKING**: Moved `griptape.common.observable.observable` to `griptape.common.decorators.observable`.
- **BREAKING**: `AnthropicDriversConfig` no longer bundles `VoyageAiEmbeddingDriver`.
- **BREAKING**: Removed `HuggingFaceHubPromptDriver.params`, use `HuggingFaceHubPromptDriver.extra_params` instead.
- **BREAKING**: Removed `HuggingFacePipelinePromptDriver.params`, use `HuggingFacePipelinePromptDriver.extra_params` instead.
- **BREAKING**: Renamed `BaseTask.run` to `BaseTask.try_run`.
- **BREAKING**: Renamed `BaseTask.execute` to `BaseTask.run`.
- **BREAKING**: Renamed `BaseTask.can_execute` to `BaseTool.can_run`.
- **BREAKING**: Renamed `BaseTool.run` to `BaseTool.try_run`.
- **BREAKING**: Renamed `BaseTool.execute` to `BaseTool.run`.
- **BREAKING**: Renamed callables throughout the framework for consistency:
  - Renamed `LocalStructureRunDriver.structure_factory_fn` to `LocalStructureRunDriver.create_structure`.
  - Renamed `SnowflakeSqlDriver.connection_func` to `SnowflakeSqlDriver.get_connection`.
  - Renamed `CsvLoader.formatter_fn` to `CsvLoader.format_row`.
  - Renamed `SqlLoader.formatter_fn` to `SqlLoader.format_row`.
  - Renamed `CsvExtractionEngine.system_template_generator` to `CsvExtractionEngine.generate_system_template`.
  - Renamed `CsvExtractionEngine.user_template_generator` to `CsvExtractionEngine.generate_user_template`.
  - Renamed `JsonExtractionEngine.system_template_generator` to `JsonExtractionEngine.generate_system_template`.
  - Renamed `JsonExtractionEngine.user_template_generator` to `JsonExtractionEngine.generate_user_template`.
  - Renamed `PromptResponseRagModule.generate_system_template` to `PromptResponseRagModule.generate_system_template`.
  - Renamed `PromptTask.generate_system_template` to `PromptTask.generate_system_template`.
  - Renamed `ToolkitTask.generate_assistant_subtask_template` to `ToolkitTask.generate_assistant_subtask_template`.
  - Renamed `JsonSchemaRule.template_generator` to `JsonSchemaRule.generate_template`.
  - Renamed `ToolkitTask.generate_user_subtask_template` to `ToolkitTask.generate_user_subtask_template`.
  - Renamed `TextLoaderRetrievalRagModule.process_query_output_fn` to `TextLoaderRetrievalRagModule.process_query_output`.
  - Renamed `FuturesExecutorMixin.futures_executor_fn` to `FuturesExecutorMixin.create_futures_executor`.
  - Renamed `VectorStoreTool.process_query_output_fn` to `VectorStoreTool.process_query_output`.
  - Renamed `CodeExecutionTask.run_fn` to `CodeExecutionTask.on_run`.
  - Renamed `Chat.input_fn` to `Chat.handle_input`.
  - Renamed `Chat.output_fn` to `Chat.handle_output`.
  - Renamed `EventListener.handler` to `EventListener.on_event`.
- Updated `EventListener.handler` return type to `Optional[BaseEvent | dict]`.
- `BaseTask.parent_outputs` type has changed from `dict[str, str | None]` to `dict[str, BaseArtifact]`.
- `Workflow.context["parent_outputs"]` type has changed from `dict[str, str | None]` to `dict[str, BaseArtifact]`.
- `Pipeline.context["parent_output"]` has changed type from `str | None` to `BaseArtifact | None`.
- `_DefaultsConfig.logging_config` and `Defaults.drivers_config` are now lazily instantiated.
- `griptape.schemas.BaseSchema` now uses `griptape.schemas.UnionField` for `Union` fields.
- `BaseTask.add_parent`/`BaseTask.add_child` now only add the parent/child task to the structure if it is not already present.
- `BaseEventListener.flush_events()` to flush events from an Event Listener.
- `BaseEventListener` no longer requires a thread lock for batching events.
- Updated `ToolkitTask` system prompt to retry/fix actions when using native tool calling.
- `Chat` input now uses a slightly customized version of `Rich.prompt.Prompt` by default.
- `Chat` output now uses `Rich.print` by default.
- `Chat.output_fn`'s now takes an optional kwarg parameter, `stream`.
- Implemented `SerializableMixin` in `Structure`, `BaseTask`, `BaseTool`, and `TaskMemory`
- `@activity` decorated functions can now accept kwargs that are defined in the activity schema.
- Updated `ToolkitTask` system prompt to no longer mention `memory_name` and `artifact_namespace`.
- Models in `ToolkitTask` with native tool calling no longer need to provide their final answer as `Answer:`.
- `EventListener.event_types` will now listen on child types of any provided type.
- Only install Tool dependencies if the Tool provides a `requirements.txt` and the dependencies are not already met.
- Implemented `RunnableMixin` in `Structure`, `BaseTask`, and `BaseTool`.
- `EventBus`'s Event Listeners are now thread/coroutine-local. Event Listeners from the spawning thread will be automatically copied when using concurrent griptape features like Workflows.

### Fixed

- Structures not flushing events when not listening for `FinishStructureRunEvent`.
- `EventListener.event_types` and the argument to `BaseEventListenerDriver.handler` being out of sync.
- Models occasionally hallucinating `memory_name` and `artifact_namespace` into Tool schemas when using `ToolkitTask`.
- Models occasionally providing overly succinct final answers when using `ToolkitTask`.
- Exception getting raised in `FuturesExecutorMixin.__del__`.
- Issues when using `EventListener` as a context manager in a multi-threaded environment.

## [0.33.1] - 2024-10-11

### Fixed

- Pinned `cohere` at `~5.11.0` to resolve slow dependency resolution.
- Missing `exa-py` from `all` extra.

## [0.33.0] - 2024-10-09

## Added

- `Workflow.input_tasks` and `Workflow.output_tasks` to access the input and output tasks of a Workflow.
- Ability to pass nested list of `Tasks` to `Structure.tasks` allowing for more complex declarative Structure definitions.
- `TavilyWebSearchDriver` to integrate Tavily's web search capabilities.
- `ExaWebSearchDriver` to integrate Exa's web search capabilities.
- `Workflow.outputs` to access the outputs of a Workflow.
- `BaseFileLoader` for Loaders that load from a path.
- `BaseLoader.fetch()` method for fetching data from a source.
- `BaseLoader.parse()` method for parsing fetched data.
- `BaseFileManager.encoding` to specify the encoding when loading and saving files.
- `BaseWebScraperDriver.extract_page()` method for extracting data from an already scraped web page.
- `TextLoaderRetrievalRagModule.chunker` for specifying the chunking strategy.
- `file_utils.get_mime_type` utility for getting the MIME type of a file.
- `BaseRulesetDriver` for loading a `Ruleset` from an external source.
  - `LocalRulesetDriver` for loading a `Ruleset` from a local `.json` file.
  - `GriptapeCloudRulesetDriver` for loading a `Ruleset` resource from Griptape Cloud.
- Parameter `alias` on `GriptapeCloudConversationMemoryDriver` for fetching a Thread by alias.
- Basic support for OpenAi Structured Output via `OpenAiChatPromptDriver.response_format` parameter.
- Ability to pass callable to `activity.schema` for dynamic schema generation.

### Changed

- **BREAKING**: Renamed parameters on several classes to `client`:
  - `bedrock_client` on `AmazonBedrockCohereEmbeddingDriver`.
  - `bedrock_client` on `AmazonBedrockCohereEmbeddingDriver`.
  - `bedrock_client` on `AmazonBedrockTitanEmbeddingDriver`.
  - `bedrock_client` on `AmazonBedrockImageGenerationDriver`.
  - `bedrock_client` on `AmazonBedrockImageQueryDriver`.
  - `bedrock_client` on `AmazonBedrockPromptDriver`.
  - `sagemaker_client` on `AmazonSageMakerJumpstartEmbeddingDriver`.
  - `sagemaker_client` on `AmazonSageMakerJumpstartPromptDriver`.
  - `sqs_client` on `AmazonSqsEventListenerDriver`.
  - `iotdata_client` on `AwsIotCoreEventListenerDriver`.
  - `s3_client` on `AmazonS3FileManagerDriver`.
  - `s3_client` on `AwsS3Tool`.
  - `iam_client` on `AwsIamTool`.
  - `pusher_client` on `PusherEventListenerDriver`.
  - `mq` on `MarqoVectorStoreDriver`.
  - `model_client` on `GooglePromptDriver`.
  - `model_client` on `GoogleTokenizer`.
- **BREAKING**: Renamed parameter `pipe` on `HuggingFacePipelinePromptDriver` to `pipeline`.
- **BREAKING**: Removed `BaseFileManager.default_loader` and `BaseFileManager.loaders`.
- **BREAKING**: Loaders no longer chunk data, use a Chunker to chunk the data.
- **BREAKING**: Removed `fileutils.load_file` and `fileutils.load_files`.
- **BREAKING**: Removed `loaders-dataframe` and `loaders-audio` extras as they are no longer needed.
- **BREKING**: `TextLoader`, `PdfLoader`, `ImageLoader`, and `AudioLoader` now take a `str | PathLike` instead of `bytes`. Passing `bytes` is still supported but deprecated.
- **BREAKING**: Removed `DataframeLoader`.
- **BREAKING**: Update `pypdf` dependency to `^5.0.1`.
- **BREAKING**: Update `redis` dependency to `^5.1.0`.
- **BREAKING**: Remove `torch` extra from `transformers` dependency. This must be installed separately.
- **BREAKING**: Split `BaseExtractionEngine.extract` into `extract_text` and `extract_artifacts` for consistency with `BaseSummaryEngine`.
- **BREAKING**: `BaseExtractionEngine` no longer catches exceptions and returns `ErrorArtifact`s.
- **BREAKING**: `JsonExtractionEngine.template_schema` is now required.
- **BREAKING**: `CsvExtractionEngine.column_names` is now required.
- **BREAKING**: Renamed`RuleMixin.all_rulesets` to `RuleMixin.rulesets`.
- **BREAKING**: Renamed `GriptapeCloudKnowledgeBaseVectorStoreDriver` to `GriptapeCloudVectorStoreDriver`.
- **BREAKING**: `OpenAiChatPromptDriver.response_format` is now a `dict` instead of a `str`.
- `MarkdownifyWebScraperDriver.DEFAULT_EXCLUDE_TAGS` now includes media/blob-like HTML tags
- `StructureRunTask` now inherits from `PromptTask`.
- Several places where API clients are initialized are now lazy loaded.
- `BaseVectorStoreDriver.upsert_text_artifacts` now returns a list or dictionary of upserted vector ids.
- `LocalFileManagerDriver.workdir` is now optional.
- `filetype` is now a core dependency.
- `FileManagerTool` now uses `filetype` for more accurate file type detection.
- `BaseFileLoader.load_file()` will now either return a `TextArtifact` or a `BlobArtifact` depending on whether `BaseFileManager.encoding` is set.
- `Structure.output`'s type is now `BaseArtifact` and raises an exception if the output is `None`.
- `JsonExtractionEngine.extract_artifacts` now returns a `ListArtifact[JsonArtifact]`.
- `CsvExtractionEngine.extract_artifacts` now returns a `ListArtifact[CsvRowArtifact]`.
- Remove `manifest.yml` requirements for custom tool creation.

### Fixed

- Anthropic native Tool calling.
- Empty `ActionsSubtask.thought` being logged.
- `RuleMixin` no longer prevents setting `rulesets` _and_ `rules` at the same time.
- `PromptTask` will merge in its Structure's Rulesets and Rules.
- `PromptTask` not checking whether Structure was set before building Prompt Stack.
- `BaseTask.full_context` context being empty when not connected to a Structure.
- Tool calling when using `OpenAiChatPromptDriver` with Groq.

## [0.32.0] - 2024-09-17

### Added

- `BaseArtifact.to_bytes()` method to convert an Artifact's value to bytes.
- `BlobArtifact.base64` property for converting a `BlobArtifact`'s value to a base64 string.
- `CsvLoader`/`SqlLoader`/`DataframeLoader` `formatter_fn` field for customizing how SQL results are formatted into `TextArtifact`s.
- `AzureOpenAiTextToSpeechDriver`.
- `JsonSchemaRule` for instructing the LLM to output a JSON object that conforms to a schema.
- Ability to use Event Listeners as Context Managers for temporarily setting the Event Bus listeners.
- Ability to use Drivers Configs as Context Managers for temporarily setting the default Drivers.
- Generic type support to `ListArtifact`.
- Iteration support to `ListArtifact`.

### Changed

- **BREAKING**: Removed `CsvRowArtifact`. Use `TextArtifact` instead.
- **BREAKING**: Removed `DataframeLoader`.
- **BREAKING**: Removed `MediaArtifact`, use `ImageArtifact` or `AudioArtifact` instead.
- **BREAKING**: `CsvLoader` and `SqlLoader` now return `ListArtifact[TextArtifact]`.
- **BREAKING**: Removed `ImageArtifact.media_type`.
- **BREAKING**: Removed `AudioArtifact.media_type`.
- **BREAKING**: Removed `BlobArtifact.dir_name`.
- **BREAKING**: Moved `ImageArtifact.prompt` and `ImageArtifact.model` into `ImageArtifact.meta`.
- **BREAKING**: `ImageArtifact.format` is now required.
- **BREAKING**: Removed the `__all__` declaration from the `griptape.mixins` module.
- Updated `JsonArtifact` value converter to properly handle more types.
- `AudioArtifact` now subclasses `BlobArtifact` instead of `MediaArtifact`.
- `ImageArtifact` now subclasses `BlobArtifact` instead of `MediaArtifact`.
- Removed `__add__` method from `BaseArtifact`, implemented it where necessary.

### Fixed

- Crash when passing "empty" Artifacts or no Artifacts to `CohereRerankDriver`.

## [0.31.0] - 2024-09-03

**Note**: This release includes breaking changes. Please refer to the [Migration Guide](./MIGRATION.md#030x-to-031x) for details.

### Added

- Parameter `meta: dict` on `BaseEvent`.
- `AzureOpenAiTextToSpeechDriver`.
- Ability to use Event Listeners as Context Managers for temporarily setting the Event Bus listeners.
- `JsonSchemaRule` for instructing the LLM to output a JSON object that conforms to a schema.
- Ability to use Drivers Configs as Context Managers for temporarily setting the default Drivers.

### Changed

- **BREAKING**: Drivers, Loaders, and Engines now raise exceptions rather than returning `ErrorArtifacts`.
- **BREAKING**: Parameter `driver` on `BaseConversationMemory` renamed to `conversation_memory_driver`.
- **BREAKING**: `BaseConversationMemory.add_to_prompt_stack` now takes a `prompt_driver` parameter.
- **BREAKING**: `BaseConversationMemoryDriver.load` now returns `tuple[list[Run], dict]`. This represents the runs and metadata.
- **BREAKING**: `BaseConversationMemoryDriver.store` now takes `runs: list[Run]` and `metadata: dict` as input.
- **BREAKING**: Parameter `file_path` on `LocalConversationMemoryDriver` renamed to `persist_file` and is now type `Optional[str]`.
- **BREAKING**: Removed the `__all__` declaration from the `griptape.mixins` module.
- `Defaults.drivers_config.conversation_memory_driver` now defaults to `LocalConversationMemoryDriver` instead of `None`.
- `CsvRowArtifact.to_text()` now includes the header.

### Fixed

- Parsing streaming response with some OpenAI compatible services.
- Issue in `PromptSummaryEngine` if there are no artifacts during recursive summarization.
- Issue in `GooglePromptDriver` using Tools with no schema.
- Missing `maxTokens` inference parameter in `AmazonBedrockPromptDriver`.
- Incorrect model in `OpenAiDriverConfig`'s `text_to_speech_driver`.
- Crash when using `CohereRerankDriver` with `CsvRowArtifact`s.
- Crash when passing "empty" Artifacts or no Artifacts to `CohereRerankDriver`.

## [0.30.2] - 2024-08-26

### Fixed

- Ensure thread safety when publishing events by adding a thread lock to batch operations in `BaseEventListenerDriver`.
- `FileManagerTool` failing to save Artifacts created by `ExtractionTool` with a `CsvExtractionEngine`.

## [0.30.1] - 2024-08-21

### Fixed

- `CsvExtractionEngine` not using provided `Ruleset`s.
- Docs examples for Extraction Engines not properly passing in schemas.

## [0.30.0] - 2024-08-20

### Added

- `AstraDbVectorStoreDriver` to support DataStax Astra DB as a vector store.
- Ability to set custom schema properties on Tool Activities via `extra_schema_properties`.
- Parameter `structure` to `BaseTask`.
- Method `try_find_task` to `Structure`.
- `TranslateQueryRagModule` `RagEngine` module for translating input queries.
- Global event bus, `griptape.events.EventBus`, for publishing and subscribing to events.
- Global object, `griptape.configs.Defaults`, for setting default values throughout the framework.
- Unique name generation for all `RagEngine` modules.
- `ExtractionTool` for having the LLM extract structured data from text.
- `PromptSummaryTool` for having the LLM summarize text.
- `QueryTool` for having the LLM query text.
- Support for bitshift composition in `BaseTask` for adding parent/child tasks.
- `JsonArtifact` for handling de/seralization of values.
- `Chat.logger_level` for setting what the `Chat` utility sets the logger level to.
- `FuturesExecutorMixin` to DRY up and optimize concurrent code across multiple classes.
- `utils.execute_futures_list_dict` for executing a dict of lists of futures.
- `GriptapeCloudConversationMemoryDriver` to store conversation history in Griptape Cloud.
- `griptape.utils.decorators.lazy_property` for creating lazy properties.

### Changed

- **BREAKING**: Removed all uses of `EventPublisherMixin` in favor of `EventBus`.
- **BREAKING**: Removed `EventPublisherMixin`.
- **BREAKING**: Removed `Pipeline.prompt_driver` and `Workflow.prompt_driver`. Set this via `griptape.configs.Defaults.drivers.prompt_driver` instead. `Agent.prompt_driver` has not been removed.
- **BREAKING**: Removed `Pipeline.stream` and `Workflow.stream`. Set this via `griptape.configs.Defaults.drivers.prompt_driver.stream` instead. `Agent.stream` has not been removed.
- **BREAKING**: Removed `Structure.embedding_driver`, set this via `griptape.configs.Defaults.drivers.embedding_driver` instead.
- **BREAKING**: Removed `Structure.custom_logger` and `Structure.logger_level`, set these via `logging.getLogger(griptape.configs.Defaults.logger_name)` instead.
- **BREAKING**: Removed `BaseStructureConfig.merge_config`.
- **BREAKING**: Renamed `StructureConfig` to `DriversConfig`, moved to `griptape.configs.drivers` and renamed fields accordingly.
- **BREAKING**: `RagContext.output` was changed to `RagContext.outputs` to support multiple outputs. All relevant RAG modules were adjusted accordingly.
- **BREAKING**: Removed before and after response modules from `ResponseRagStage`.
- **BREAKING**: Moved ruleset and metadata ingestion from standalone modules to `PromptResponseRagModule`.
- **BREAKING**: Dropped `Client` from all Tool names for better naming consistency.
- **BREAKING**: Dropped `_client` suffix from all Tool packages.
- **BREAKING**: Added `Tool` suffix to all Tool names for better naming consistency.
- **BREAKING**: Removed `TextArtifactStorage.query` and `TextArtifactStorage.summarize`.
- **BREAKING**: Removed `TextArtifactStorage.rag_engine`, and `TextArtifactStorage.retrieval_rag_module_name`.
- **BREAKING**: Removed `TextArtifactStorage.summary_engine`, `TextArtifactStorage.csv_extraction_engine`, and `TextArtifactStorage.json_extraction_engine`.
- **BREAKING**: Removed `TaskMemory.summarize_namespace` and `TaskMemory.query_namespace`.
- **BREAKING**: Removed `Structure.rag_engine`.
- **BREAKING**: Split `JsonExtractionEngine.template_generator` into `JsonExtractionEngine.system_template_generator` and `JsonExtractionEngine.user_template_generator`.
- **BREAKING**: Split `CsvExtractionEngine.template_generator` into `CsvExtractionEngine.system_template_generator` and `CsvExtractionEngine.user_template_generator`.
- **BREAKING**: Changed `JsonExtractionEngine.template_schema` from a `run` argument to a class attribute.
- **BREAKING**: Changed `CsvExtractionEngine.column_names` from a `run` argument to a class attribute.
- **BREAKING**: Removed `JsonExtractionTask`, and `CsvExtractionTask` use `ExtractionTask` instead.
- **BREAKING**: Removed `TaskMemoryClient`, use `QueryClient`, `ExtractionTool`, or `PromptSummaryTool` instead.
- **BREAKING**: `BaseTask.add_parent/child` now take a `BaseTask` instead of `str | BaseTask`.
- Engines that previously required Drivers now pull from `griptape.configs.Defaults.drivers_config` by default.
- `BaseTask.add_parent/child` will now call `self.structure.add_task` if possible.
- `BaseTask.add_parent/child` now returns `self`, allowing for chaining.
- `Chat` now sets the `griptape` logger level to `logging.ERROR`, suppressing all logs except for errors.

### Fixed

- `JsonExtractionEngine` failing to parse json when the LLM outputs more than just the json.
- Exception when adding `ErrorArtifact`'s to the Prompt Stack.
- Concurrency bug in `BaseVectorStoreDriver.upsert_text_artifacts`.
- Schema issues with Tools that use lists.
- Issue with native Tool calling and streaming with `GooglePromptDriver`.
- Description not being used properly in `StructureRunTool`.

## [0.29.2] - 2024-08-16

### Fixed

- `Workflow` threads not being properly cleaned up after completion.
- Crash when `ToolAction`s were missing output due to an `ActionsSubtask` exception.

## [0.29.1] - 2024-08-02

### Changed

- Remove `BaseTextArtifact`, revert `CsvRowArtifact` to subclass `TextArtifact`.

### Fixed

- Missing extra for `drivers-text-to-speech-elevenlabs`.

## [0.29.0] - 2024-07-30

### Added

- Native function calling support to `OpenAiChatPromptDriver`, `AzureOpenAiChatPromptDriver`, `AnthropicPromptDriver`, `AmazonBedrockPromptDriver`, `GooglePromptDriver`, `OllamaPromptDriver`, and `CoherePromptDriver`.
- `OllamaEmbeddingDriver` for generating embeddings with Ollama.
- `GriptapeCloudKnowledgeBaseVectorStoreDriver` to query Griptape Cloud Knowledge Bases.
- `GriptapeCloudEventListenerDriver.api_key` defaults to the value in the `GT_CLOUD_API_KEY` environment variable.
- `BaseObservabilityDriver` as the base class for all Observability Drivers.
- `DummyObservabilityDriver` as a no-op Observability Driver.
- `OpenTelemetryObservabilityDriver` for sending observability data to an open telemetry collector or vendor.
- `GriptapeCloudObservabilityDriver` for sending observability data to Griptape Cloud.
- `DatadogObservabilityDriver` for sending observability data to a Datadog Agent.
- `Observability` context manager for enabling observability and configuring which Observability Driver to use.
- `@observable` decorator for selecting which functions/methods to provide observability for.
- `GenericArtifact` for storing any data.
- `BaseTextArtifact` for text-based Artifacts to subclass.
- `HuggingFacePipelineImageGenerationDriver` for generating images locally with HuggingFace pipelines.
- `BaseImageGenerationPipelineDriver` as the base class for drivers interfacing with HuggingFace image generation pipelines.
- `StableDiffusion3ImageGenerationPipelineDriver` for local text-to-image generation using a Stable Diffusion 3 pipeline.
- `StableDiffusion3Img2ImgImageGenerationPipelineDriver` for local image-to-image generation using a Stable Diffusion 3 pipeline.
- `StableDiffusion3ControlNetImageGenerationPipelineDriver` for local ControlNet image generation using a Stable Diffusion 3 pipeline.
- Optional `params` field to `WebSearch`'s `search` schema that the LLM can be steered into using.

### Changed

- **BREAKING**: `BaseVectorStoreDriver.upsert_text_artifacts` optional arguments are now keyword-only arguments.
- **BREAKING**: `BaseVectorStoreDriver.upsert_text_artifact` optional arguments are now keyword-only arguments.
- **BREAKING**: `BaseVectorStoreDriver.upsert_text` optional arguments are now keyword-only arguments.
- **BREAKING**: `BaseVectorStoreDriver.does_entry_exist` optional arguments are now keyword-only arguments.
- **BREAKING**: `BaseVectorStoreDriver.load_artifacts` optional arguments are now keyword-only arguments.
- **BREAKING**: `BaseVectorStoreDriver.upsert_vector` optional arguments are now keyword-only arguments.
- **BREAKING**: `BaseVectorStoreDriver.query` optional arguments are now keyword-only arguments.
- **BREAKING**: `EventListener.publish_event`'s `flush` argument is now a keyword-only argument.
- **BREAKING**: `BaseEventListenerDriver.publish_event`'s `flush` argument is now a keyword-only argument.
- **BREAKING**: Renamed `DummyException` to `DummyError` for pep8 naming compliance.
- **BREAKING**: Migrate to `sqlalchemy` 2.0.
- **BREAKING**: Make `sqlalchemy` an optional dependency.
- **BREAKING**: Renamed `drivers-sql-redshift` to `drivers-sql-amazon-redshift`
- **BREAKING**: Renamed `drivers-prompt-huggingface` extra to `drivers-prompt-huggingface-hub`.
- **BREAKING**: Renamed `drivers-vector-postgresql` extra to `drivers-vector-pgvector`.
- **BREAKING**: Update `marqo` dependency to `^3.7.0`.
- **BREAKING**: Removed `drivers-sql-postgresql` extra. Use `drivers-sql` extra and install necessary drivers (i.e. `psycopg2`) separately.
- **BREAKING**: `api_key` and `search_id` are now required fields in `GoogleWebSearchDriver`.
- **BREAKING**: `web_search_driver` is now required fields in the `WebSearch` Tool.
- `GoogleWebSearchDriver` and `DuckDuckGoWebSearchDriver` now use `kwargs` passed to the `run` method.
- Removed unnecessary `sqlalchemy-redshift` dependency in `drivers-sql-amazon-redshift` extra.
- Removed unnecessary `transformers` dependency in `drivers-prompt-huggingface` extra.
- Removed unnecessary `huggingface-hub` dependency in `drivers-prompt-huggingface-pipeline` extra.
- `CsvRowArtifact` now inherits from `BaseTextArtifact`.
- `TextArtifact` now inherits from `BaseTextArtifact`.

### Fixed

- Parameter `count` for `QdrantVectorStoreDriver.query` now optional as per documentation.
- Path issues on Windows with `LocalFileManagerDriver` and `AmazonS3FileManagerDriver`.

## [0.28.2] - 2024-07-12

### Fixed

- Conversation Memory being incorrectly inserted into the `PromptTask.prompt_stack` when no system content is present.

## [0.28.1] - 2024-07-10

### Fixed

- Sending empty system content in `PromptTask`.
- Throttling issues with `DuckDuckGoWebSearchDriver`.

## [0.28.0] - 2024-07-09

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
      - `TextLoaderRetrievalRagModule` for retrieving data with text loaders in real time.
      - `TextChunksRerankRagModule` for re-ranking retrieved results.
    - Response:
      - `MetadataBeforeResponseRagModule` for appending metadata.
      - `RulesetsBeforeResponseRagModule` for appending rulesets.
      - `PromptResponseRagModule` for generating responses based on retrieved text chunks.
      - `TextChunksResponseRagModule` for responding with retrieved text chunks.
      - `FootnotePromptResponseRagModule` for responding with automatic footnotes from text chunk references.
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
- Parameters `sort_key` and `sort_key_value` on `AmazonDynamoDbConversationMemoryDriver` for tables with sort keys.
- `Reference` for supporting artifact citations in loaders and RAG engine modules.

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
- `GriptapeCloudStructureRunDriver` now outputs a `BaseArtifact` instead of a `TextArtifact`

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
- `ImageQueryTool` allowing an Agent to make queries on images on disk or in Task Memory.
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
