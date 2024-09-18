---
search:
  boost: 2 
---

## Overview

Loaders are used to load textual data from different sources and chunk it into [TextArtifact](../../reference/griptape/artifacts/text_artifact.md)s.
Each loader can be used to load a single "document" with [load()](../../reference/griptape/loaders/base_loader.md#griptape.loaders.base_loader.BaseLoader.load) or
multiple documents with [load_collection()](../../reference/griptape/loaders/base_loader.md#griptape.loaders.base_loader.BaseLoader.load_collection).

## PDF

!!! info
    This driver requires the `loaders-pdf` [extra](../index.md#extras).

Inherits from the [TextLoader](../../reference/griptape/loaders/text_loader.md) and can be used to load PDFs from a path or from an IO stream:

```python
--8<-- "docs/griptape-framework/data/src/loaders_1.py"
```

## SQL

Can be used to load data from a SQL database into [TextArtifact](../../reference/griptape/artifacts/text_artifact.md)s:

```python
--8<-- "docs/griptape-framework/data/src/loaders_2.py"
```

## CSV

Can be used to load CSV files into [TextArtifact](../../reference/griptape/artifacts/text_artifact.md)s:

```python
--8<-- "docs/griptape-framework/data/src/loaders_3.py"
```


## DataFrame

!!! info
    This driver requires the `loaders-dataframe` [extra](../index.md#extras).

Can be used to load [pandas](https://pandas.pydata.org/) [DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html)s into [TextArtifact](../../reference/griptape/artifacts/text_artifact.md)s:

```python
--8<-- "docs/griptape-framework/data/src/loaders_4.py"
```


## Text

Used to load arbitrary text and text files:

```python
--8<-- "docs/griptape-framework/data/src/loaders_5.py"
```

You can set a custom [tokenizer](../../reference/griptape/loaders/text_loader.md#griptape.loaders.text_loader.TextLoader.tokenizer), [max_tokens](../../reference/griptape/loaders/text_loader.md#griptape.loaders.text_loader.TextLoader.max_tokens) parameter, and [chunker](../../reference/griptape/loaders/text_loader.md#griptape.loaders.text_loader.TextLoader.chunker).

## Web

!!! info
    This driver requires the `loaders-web` [extra](../index.md#extras).

Inherits from the [TextLoader](../../reference/griptape/loaders/text_loader.md) and can be used to load web pages:

```python
--8<-- "docs/griptape-framework/data/src/loaders_6.py"
```

## Image

!!! info
    This driver requires the `loaders-image` [extra](../index.md#extras).

The Image Loader is used to load an image as an [ImageArtifact](./artifacts.md#image). The Loader operates on image bytes that can be sourced from files on disk, downloaded images, or images in memory.

```python
--8<-- "docs/griptape-framework/data/src/loaders_7.py"
```

By default, the Image Loader will load images in their native format, but not all models work on all formats. To normalize the format of Artifacts returned by the Loader, set the `format` field.

```python
--8<-- "docs/griptape-framework/data/src/loaders_8.py"
```


## Email

!!! info
    This driver requires the `loaders-email` [extra](../index.md#extras).

Can be used to load email from an imap server:

```python
--8<-- "docs/griptape-framework/data/src/loaders_9.py"
```

## Audio

!!! info
    This driver requires the `loaders-audio` [extra](../index.md#extras).

The [Audio Loader](../../reference/griptape/loaders/audio_loader.md) is used to load audio content as an [AudioArtifact](./artifacts.md#audio). The Loader operates on audio bytes that can be sourced from files on disk, downloaded audio, or audio in memory.

The Loader will load audio in its native format and populates the resulting Artifact's `format` field by making a best-effort guess of the underlying audio format using the `filetype` package.

```python
--8<-- "docs/griptape-framework/data/src/loaders_10.py"
```
