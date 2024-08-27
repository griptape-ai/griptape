---
search:
  boost: 2 
---

## Overview


**[Artifacts](../../reference/griptape/artifacts/base_artifact.md)** are used to store data that can be provided as input to or received as output from a Language Learning Model (LLM).

## Text

[TextArtifact](../../reference/griptape/artifacts/text_artifact.md)s store textual data. They can be used to count tokens using the [token_count()](../../reference/griptape/artifacts/text_artifact.md#griptape.artifacts.text_artifact.TextArtifact.token_count) method with a tokenizer, generate a text embedding through the [generate_embedding()](../../reference/griptape/artifacts/text_artifact.md#griptape.artifacts.text_artifact.TextArtifact.generate_embedding) method, and access the embedding with the [embedding](../../reference/griptape/artifacts/text_artifact.md#griptape.artifacts.text_artifact.TextArtifact.embedding) property.

[TaskMemory](../../reference/griptape/memory/task/task_memory.md) automatically stores `TextArtifacts` returned by tool activities and provides their IDs back to the LLM.

## Image

[ImageArtifact](../../reference/griptape/artifacts/image_artifact.md)s store image data. They include binary image data and metadata such as MIME type, dimensions, and prompt and model information for images returned by [image generation drivers](../drivers/image-generation-drivers.md). They inherit functionality from [BlobArtifacts](#blob).

## Audio

[AudioArtifact](../../reference/griptape/artifacts/audio_artifact.md)s store audio content, including binary audio data and metadata such as format, duration, and prompt and model information for audio returned by generative models. They inherit from [BlobArtifacts](#blob).

## Action

[ActionArtifact](../../reference/griptape/artifacts/action_artifact.md)s represent actions taken by the LLM. Currently, the only supported action is [ToolAction](../../reference/griptape/common/actions/tool_action.md), which is used to execute a [Tool](../../griptape-framework/tools/index.md).

## JSON

[JsonArtifact](../../reference/griptape/artifacts/json_artifact.md)s store JSON-serializable data. Any data assigned to the `value` property is converted using `json.dumps(json.loads(value))`.

## Generic

[GenericArtifact](../../reference/griptape/artifacts/generic_artifact.md)s act as an escape hatch for passing any type of data that does not fit into any other artifact type. While generally not recommended, they are suitable for specific scenarios. For example, see [talking to a video](../../examples/talk-to-a-video.md), which demonstrates using a `GenericArtifact` to pass a Gemini-specific video file.

## System Artifacts

These Artifacts don't map to an LLM modality. They must be transformed in some way before they can be used as LLM input.

### Blob

[BlobArtifact](../../reference/griptape/artifacts/blob_artifact.md)s store binary large objects (blobs) and are used to pass unstructured data back to the LLM via [InfoArtifact](#info).

`TaskMemory` automatically stores `BlobArtifacts` returned by tool activities, allowing them to be reused by other tools.

### Info

[InfoArtifact](../../reference/griptape/artifacts/info_artifact.md)s store short notifications that are passed back to the LLM without being stored in Task Memory.

### Error

[ErrorArtifact](../../reference/griptape/artifacts/error_artifact.md)s store errors that are passed back to the LLM without being stored in Task Memory.

### List

[ListArtifact](../../reference/griptape/artifacts/list_artifact.md)s store lists of Artifacts that can be passed to the LLM.

