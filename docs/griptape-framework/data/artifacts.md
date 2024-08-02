---
search:
  boost: 2 
---

## Overview

**[Artifacts](../../reference/griptape/artifacts/base_artifact.md)** are used for passing different types of data between Griptape components. All tools return artifacts that are later consumed by tasks and task memory. 
Artifacts make sure framework components enforce contracts when passing and consuming data.

## Text

A [TextArtifact](../../reference/griptape/artifacts/text_artifact.md) for passing text data of arbitrary size around the framework. It can be used to count tokens with [token_count()](../../reference/griptape/artifacts/text_artifact.md#griptape.artifacts.text_artifact.TextArtifact.token_count) with a tokenizer. 
It can also be used to generate a text embedding with [generate_embedding()](../../reference/griptape/artifacts/text_artifact.md#griptape.artifacts.text_artifact.TextArtifact.generate_embedding) 
and access it with [embedding](../../reference/griptape/artifacts/text_artifact.md#griptape.artifacts.text_artifact.TextArtifact.embedding).

[TaskMemory](../../reference/griptape/memory/task/task_memory.md) automatically stores [TextArtifact](../../reference/griptape/artifacts/text_artifact.md)s returned by tool activities and returns artifact IDs back to the LLM.

## Csv Row

A [CsvRowArtifact](../../reference/griptape/artifacts/csv_row_artifact.md) for passing structured row data around the framework. It inherits from [TextArtifact](../../reference/griptape/artifacts/text_artifact.md) and overrides the 
[to_text()](../../reference/griptape/artifacts/csv_row_artifact.md#griptape.artifacts.csv_row_artifact.CsvRowArtifact.to_text) method, which always returns a valid CSV row.

## Info

An [InfoArtifact](../../reference/griptape/artifacts/info_artifact.md) for passing short notifications back to the LLM without task memory storing them.

## Error

An [ErrorArtifact](../../reference/griptape/artifacts/error_artifact.md) is used for passing errors back to the LLM without task memory storing them.

## Blob

A [BlobArtifact](../../reference/griptape/artifacts/blob_artifact.md) for passing binary large objects (blobs) back to the LLM. 
Treat it as a way to return unstructured data, such as images, videos, audio, and other files back from tools. 
Each blob has a [name](../../reference/griptape/artifacts/base_artifact.md#griptape.artifacts.base_artifact.BaseArtifact.name) and 
[dir](../../reference/griptape/artifacts/blob_artifact.md#griptape.artifacts.blob_artifact.BlobArtifact.dir_name) to uniquely identify stored objects.

[TaskMemory](../../reference/griptape/memory/task/task_memory.md) automatically stores [BlobArtifact](../../reference/griptape/artifacts/blob_artifact.md)s returned by tool activities that can be reused by other tools.

## Image

An [ImageArtifact](../../reference/griptape/artifacts/image_artifact.md) is used for passing images back to the LLM. In addition to binary image data, an Image Artifact includes image metadata like MIME type, dimensions, and prompt and model information for images returned by [image generation Drivers](../drivers/image-generation-drivers.md). It inherits from [BlobArtifact](#blobartifact).

## Audio

An [AudioArtifact](../../reference/griptape/artifacts/audio_artifact.md) allows the Framework to interact with audio content. An Audio Artifact includes binary audio content as well as metadata like format, duration, and prompt and model information for audio returned generative models. It inherits from [BlobArtifact](#blobartifact).

## Boolean

A [BooleanArtifact](../../reference/griptape/artifacts/boolean_artifact.md) is used for passing boolean values around the framework.

!!! info
    Any object passed on init to `BooleanArtifact` will be coerced into a `bool` type. This might lead to unintended behavior: `BooleanArtifact("False").value is True`. Use [BooleanArtifact.parse_bool](../../reference/griptape/artifacts/boolean_artifact.md#griptape.artifacts.boolean_artifact.BooleanArtifact.parse_bool) to convert case-insensitive string literal values `"True"` and `"False"` into a `BooleanArtifact`: `BooleanArtifact.parse_bool("False").value is False`.

## Generic

A [GenericArtifact](../../reference/griptape/artifacts/generic_artifact.md) can be used as an escape hatch for passing any type of data around the framework.
It is generally not recommended to use this Artifact type, but it can be used in a handful of situations where no other Artifact type fits the data being passed.
See [talking to a video](../../examples/talk-to-a-video.md) for an example of using a `GenericArtifact` to pass a Gemini-specific video file.
