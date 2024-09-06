---
search:
  boost: 2 
---

## Overview

Loaders are used to load data from sources and parse it into [Artifact](../../griptape-framework/data/artifacts.md)s.
Each loader can be used to load a single "source" with [load()](../../reference/griptape/loaders/base_loader.md#griptape.loaders.base_loader.BaseLoader.load) or
multiple sources with [load_collection()](../../reference/griptape/loaders/base_loader.md#griptape.loaders.base_loader.BaseLoader.load_collection).


## File

The following Loaders load a file using a [FileManagerDriver](../../reference/griptape/drivers/file_manager_driver.md) and loads the resulting data into an [Artifact](../../reference/griptape/artifacts/artifact.md) for the respective file type.

### Text

Loads text files into [TextArtifact](../../reference/griptape/artifacts/text_artifact.md)s:

```python
--8<-- "docs/griptape-framework/data/src/loaders_5.py"
```

### PDF

!!! info
    This driver requires the `loaders-pdf` [extra](../index.md#extras).

Loads PDF files into [ListArtifact](../../reference/griptape/artifacts/list_artifact.md)s, where each element is a [TextArtifact](../../reference/griptape/artifacts/text_artifact.md) containing a page of the PDF:

```python
--8<-- "docs/griptape-framework/data/src/loaders_1.py"
```

### CSV

Loads CSV files into [ListArtifact](../../reference/griptape/artifacts/list_artifact.md)s, where each element is a [TextArtifact](../../reference/griptape/artifacts/text_artifact.md) containing a row of the CSV:

```python
--8<-- "docs/griptape-framework/data/src/loaders_3.py"
```

### Image

!!! info
    This driver requires the `loaders-image` [extra](../index.md#extras).

Loads images into [ImageArtifact](../../reference/griptape/artifacts/image_artifact.md)s:


```python
--8<-- "docs/griptape-framework/data/src/loaders_7.py"
```

By default, the Image Loader will load images in their native format, but not all models work on all formats. To normalize the format of Artifacts returned by the Loader, set the `format` field.

```python
--8<-- "docs/griptape-framework/data/src/loaders_8.py"
```

### Audio

Loads audio files into [AudioArtifact](../../reference/griptape/artifacts/audio_artifact.md)s:

The Loader will load audio in its native format and populates the resulting Artifact's `format` field by making a best-effort guess of the underlying audio format using the `filetype` package.

```python
--8<-- "docs/griptape-framework/data/src/loaders_10.py"
```

## Web

!!! info
    This driver requires the `loaders-web` [extra](../index.md#extras).

Scrapes web pages using a [WebScraperDriver](../../reference/griptape/drivers/web_scraper_driver.md) and loads the resulting text into [TextArtifact](../../reference/griptape/artifacts/text_artifact.md)s.

```python
--8<-- "docs/griptape-framework/data/src/loaders_6.py"
```

## SQL

Loads data from a SQL database using a [SQLDriver](../../reference/griptape/drivers/sql_driver.md) and loads the resulting data into [ListArtifact](../../reference/griptape/artifacts/list_artifact.md)s, where each element is a [CsvRowArtifact](../../reference/griptape/artifacts/csv_row_artifact.md) containing a row of the SQL query.

```python
--8<-- "docs/griptape-framework/data/src/loaders_2.py"
```

## Email

!!! info
    This driver requires the `loaders-email` [extra](../index.md#extras).

Loads data from an imap email server into a [ListArtifact](../../reference/griptape/artifacts/list_artifact.md)s, where each element is a [TextArtifact](../../reference/griptape/artifacts/text_artifact.md) containing an email.

```python
--8<-- "docs/griptape-framework/data/src/loaders_9.py"
```
