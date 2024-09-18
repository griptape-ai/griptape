---
search:
  boost: 2 
---

## Overview

**[Artifacts](../../reference/griptape/artifacts/base_artifact.md)** are the core data structure in Griptape. They are used to encapsulate data and enhance it with metadata.

## Text

[TextArtifact](../../reference/griptape/artifacts/text_artifact.md)s store textual data. They offer methods such as [token_count()](../../reference/griptape/artifacts/text_artifact.md#griptape.artifacts.text_artifact.TextArtifact.token_count) for counting tokens with a tokenizer, and [generate_embedding()](../../reference/griptape/artifacts/text_artifact.md#griptape.artifacts.text_artifact.TextArtifact.generate_embedding) for creating text embeddings. You can also access the embedding via the [embedding](../../reference/griptape/artifacts/text_artifact.md#griptape.artifacts.text_artifact.TextArtifact.embedding) property.

When `TextArtifact`s are returned from Tools, they will be stored in [Task Memory](../../griptape-framework/structures/task-memory.md) if the Tool has set `off_prompt=True`.

## Blob

[BlobArtifact](../../reference/griptape/artifacts/blob_artifact.md)s store binary large objects (blobs).

When `BlobArtifact`s are returned from Tools, they will be stored in [Task Memory](../../griptape-framework/structures/task-memory.md) if the Tool has set `off_prompt=True`.

### Image

[ImageArtifact](../../reference/griptape/artifacts/image_artifact.md)s store image data. This includes binary image data along with metadata such as MIME type and dimensions. They are a subclass of [BlobArtifacts](#blob).

### Audio

[AudioArtifact](../../reference/griptape/artifacts/audio_artifact.md)s store audio content. This includes binary audio data and metadata such as format, and duration. They are a subclass of [BlobArtifacts](#blob).

## List

[ListArtifact](../../reference/griptape/artifacts/list_artifact.md)s store lists of Artifacts.

When `ListArtifact`s are returned from Tools, their elements will be stored in [Task Memory](../../griptape-framework/structures/task-memory.md) if the element is either a `TextArtifact` or a `BlobArtifact` and the Tool has set `off_prompt=True`.

## Info

[InfoArtifact](../../reference/griptape/artifacts/info_artifact.md)s store small pieces of textual information. These are useful for conveying messages about the execution or results of an operation, such as "No results found" or "Operation completed successfully."

## JSON

[JsonArtifact](../../reference/griptape/artifacts/json_artifact.md)s store JSON-serializable data. Any data assigned to the `value` property is processed using `json.dumps(json.loads(value))`.

## Error

[ErrorArtifact](../../reference/griptape/artifacts/error_artifact.md)s store exception information, providing a structured way to convey errors.

## Action

[ActionArtifact](../../reference/griptape/artifacts/action_artifact.md)s represent actions taken by an LLM. Currently, the only supported action type is [ToolAction](../../reference/griptape/common/actions/tool_action.md), which is used to execute a [Tool](../../griptape-framework/tools/index.md).

## Generic

[GenericArtifact](../../reference/griptape/artifacts/generic_artifact.md)s provide a flexible way to pass data that does not fit into any other artifact category. While not generally recommended, they can be useful for specific use cases. For instance, see [talking to a video](../../examples/talk-to-a-video.md), which demonstrates using a `GenericArtifact` to pass a Gemini-specific video file.
