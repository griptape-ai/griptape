---
search:
  boost: 2
---

## Overview

Loaders are used to load data from sources and parse it into [Artifact](../../griptape-framework/data/artifacts.md)s.
Each loader can be used to load a single "source" with [load()](../../reference/griptape/loaders/base_loader.md#griptape.loaders.base_loader.BaseLoader.load) or
multiple sources with [load_collection()](../../reference/griptape/loaders/base_loader.md#griptape.loaders.base_loader.BaseLoader.load_collection).

## File

The following Loaders load a file using a [FileManagerDriver](../../reference/griptape/drivers/file_manager/base_file_manager_driver.md) and loads the resulting data into an [Artifact](../../griptape-framework/data/artifacts.md) for the respective file type.

As a convenience, File Loaders also have a `save()` method that can save an Artifact to a destination.

```python
--8<-- "docs/griptape-framework/data/src/loaders_save.py"
```

### Text

Loads text files into [TextArtifact](../../griptape-framework/data/artifacts.md#text)s:

```python
--8<-- "docs/griptape-framework/data/src/loaders_5.py"
```

### PDF

!!! info

    This driver requires the `loaders-pdf` [extra](../index.md#extras).

Loads PDF files into [ListArtifact](../../griptape-framework/data/artifacts.md#list)s, where each element is a [TextArtifact](../../griptape-framework/data/artifacts.md#text) containing a page of the PDF:

```python
--8<-- "docs/griptape-framework/data/src/loaders_1.py"
```

### CSV

Loads CSV files into [ListArtifact](../../griptape-framework/data/artifacts.md#list)s, where each element is a [TextArtifact](../../griptape-framework/data/artifacts.md#text) containing a row of the CSV:

```python
--8<-- "docs/griptape-framework/data/src/loaders_3.py"
```

### Image

!!! info

    This driver requires the `loaders-image` [extra](../index.md#extras).

Loads images into [ImageArtifact](../../griptape-framework/data/artifacts.md#image)s:

```python
--8<-- "docs/griptape-framework/data/src/loaders_7.py"
```

By default, the Image Loader will load images in their native format, but not all models work on all formats. To normalize the format of Artifacts returned by the Loader, set the `format` field.

```python
--8<-- "docs/griptape-framework/data/src/loaders_8.py"
```

### Audio

Loads audio files into [AudioArtifact](../../griptape-framework/data/artifacts.md#audio)s:

The Loader will load audio in its native format and populates the resulting Artifact's `format` field by making a best-effort guess of the underlying audio format using the `filetype` package.

```python
--8<-- "docs/griptape-framework/data/src/loaders_10.py"
```

### JSON

Loads JSON files into [JsonArtifact](../../griptape-framework/data/artifacts.md#json)s:

```python

--8<-- "docs/griptape-framework/data/src/loaders_json.py"
```

## Web

!!! info

    This driver requires the `loaders-web` [extra](../index.md#extras).

Scrapes web pages using a [WebScraperDriver](../drivers/web-scraper-drivers.md) and loads the resulting text into [TextArtifact](../../griptape-framework/data/artifacts.md#text)s.

```python
--8<-- "docs/griptape-framework/data/src/loaders_6.py"
```

## SQL

Loads data from a SQL database using a [SQLDriver](../drivers/sql-drivers.md) and loads the resulting data into [ListArtifact](../../griptape-framework/data/artifacts.md#list)s, where each element is a [TextArtifact](../../griptape-framework/data/artifacts.md#text) containing a row of the SQL query.

```python
--8<-- "docs/griptape-framework/data/src/loaders_2.py"
```

## Email

!!! info

    This driver requires the `loaders-email` [extra](../index.md#extras).

Loads data from an imap email server into a [ListArtifact](../../reference/griptape/artifacts/list_artifact.md)s, where each element is a [TextArtifact](../../reference/griptape/artifacts/text_artifact.md) containing an email.

=== "Code"
    ```python
    --8<-- "docs/griptape-framework/data/src/loaders_9.py"
    ```

=== "Logs"
    ```python
    --8<-- "docs/griptape-framework/data/logs/loaders_9.txt"
    ```
