## Overview

Loaders are used to load textual data from different sources and chunk it into [TextArtifact](../../reference/griptape/artifacts/text_artifact.md)s.
Each loader can be used to load a single "document" with [load()](../../reference/griptape/loaders/base_loader.md#griptape.loaders.base_loader.BaseLoader.load) or
multiple documents with [load_collection()](../../reference/griptape/loaders/base_loader.md#griptape.loaders.base_loader.BaseLoader.load_collection).

## Pdf Loader

!!! info
    This driver requires the `loaders-pdf` [extra](../index.md#extras).

Inherits from the [TextLoader](../../reference/griptape/loaders/text_loader.md) and can be used to load PDFs from a path or from an IO stream:

```python
from griptape.loaders import PdfLoader
from griptape.utils import load_files, load_file
import urllib.request

urllib.request.urlretrieve("https://arxiv.org/pdf/1706.03762.pdf", "attention.pdf")

# Load a single PDF file
with open("attention.pdf", "rb") as f:
    PdfLoader().load(f.read())
# You can also use the load_file utility function
PdfLoader().load(load_file("attention.pdf"))

urllib.request.urlretrieve("https://arxiv.org/pdf/1706.03762.pdf", "CoT.pdf")

# Load multiple PDF files
with open("attention.pdf", "rb") as attention, open("CoT.pdf", "rb") as cot:
    PdfLoader().load_collection([attention.read(), cot.read()])
# You can also use the load_files utility function
PdfLoader().load_collection(list(load_files(["attention.pdf", "CoT.pdf"]).values()))
```

## Sql Loader

Can be used to load data from a SQL database into [CsvRowArtifact](../../reference/griptape/artifacts/csv_row_artifact.md)s:

```python
from griptape.loaders import SqlLoader
from griptape.drivers import SqlDriver

SqlLoader(
    sql_driver = SqlDriver(
        engine_url="sqlite:///:memory:"
    )
).load("SELECT 'foo', 'bar'")

SqlLoader(
    sql_driver = SqlDriver(
        engine_url="sqlite:///:memory:"
    )
).load_collection(["SELECT 'foo', 'bar';", "SELECT 'fizz', 'buzz';"])
```

## Csv Loader

Can be used to load CSV files into [CsvRowArtifact](../../reference/griptape/artifacts/csv_row_artifact.md)s:

```python
from griptape.loaders import CsvLoader
from griptape.utils import load_file, load_files

# Load a single CSV file
with open("tests/resources/cities.csv", "r") as f:
    CsvLoader().load(f.read())
# You can also use the load_file utility function
CsvLoader().load(load_file("tests/resources/cities.csv"))

# Load multiple CSV files
with open("tests/resources/cities.csv", "r") as cities, open("tests/resources/addresses.csv", "r") as addresses:
    CsvLoader().load_collection([cities.read(), addresses.read()])
# You can also use the load_files utility function
CsvLoader().load_collection(list(load_files(["tests/resources/cities.csv", "tests/resources/addresses.csv"]).values()))
```


## DataFrame Loader

!!! info
    This driver requires the `loaders-dataframe` [extra](../index.md#extras).

Can be used to load [pandas](https://pandas.pydata.org/) [DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html)s into [CsvRowArtifact](../../reference/griptape/artifacts/csv_row_artifact.md)s:

```python
import urllib
import pandas as pd
from griptape.loaders import DataFrameLoader

urllib.request.urlretrieve("https://people.sc.fsu.edu/~jburkardt/data/csv/cities.csv", "cities.csv")

DataFrameLoader().load(pd.read_csv("cities.csv"))

urllib.request.urlretrieve("https://people.sc.fsu.edu/~jburkardt/data/csv/addresses.csv", "addresses.csv")

DataFrameLoader().load_collection(
    [pd.read_csv('cities.csv'), pd.read_csv('addresses.csv')]
)
```


## Text Loader

Used to load arbitrary text and text files:

```python
from pathlib import Path
import urllib
from griptape.loaders import TextLoader

TextLoader().load(
    "my text"
)

urllib.request.urlretrieve("https://example-files.online-convert.com/document/txt/example.txt", "example.txt")

with open("example.txt", "r") as f:
    TextLoader().load(f.read())

with open("example.txt", "r") as f:
    TextLoader().load_collection(
        ["my text", "my other text", f.read()]
    )
```

You can set a custom [tokenizer](../../reference/griptape/loaders/text_loader.md#griptape.loaders.text_loader.TextLoader.tokenizer.md), [max_tokens](../../reference/griptape/loaders/text_loader.md#griptape.loaders.text_loader.TextLoader.max_tokens.md) parameter, and [chunker](../../reference/griptape/loaders/text_loader.md#griptape.loaders.text_loader.TextLoader.chunker.md).

## Web Loader

!!! info
    This driver requires the `loaders-web` [extra](../index.md#extras).

Inherits from the [TextLoader](../../reference/griptape/loaders/text_loader.md) and can be used to load web pages:

```python
from griptape.loaders import WebLoader

WebLoader().load(
    "https://www.griptape.ai"
)

WebLoader().load_collection(
    ["https://www.griptape.ai", "https://docs.griptape.ai"]
)
```

## Image Loader

!!! info
    This driver requires the `loaders-image` [extra](../index.md#extras).

The Image Loader is used to load an image as an [ImageArtifact](./artifacts.md#imageartifact). The Loader operates on image bytes that can be sourced from files on disk, downloaded images, or images in memory.

```python
from griptape.loaders import ImageLoader
from griptape.utils import load_file

# Load an image from disk
with open("tests/resources/mountain.png", "rb") as f:
    disk_image_artifact = ImageLoader().load(f.read())
# You can also use the load_file utility function
ImageLoader().load(load_file("tests/resources/mountain.png"))
```

By default, the Image Loader will load images in their native format, but not all models work on all formats. To normalize the format of Artifacts returned by the Loader, set the `format` field.

```python
from griptape.loaders import ImageLoader
from griptape.utils import load_files, load_file

# Load a single image in BMP format
with open("tests/resources/mountain.png", "rb") as f:
    image_artifact_jpeg = ImageLoader(format="bmp").load(f.read())
# You can also use the load_file utility function
ImageLoader(format="bmp").load(load_file("tests/resources/mountain.png"))

# Load multiple images in BMP format
with open("tests/resources/mountain.png", "rb") as mountain, open("tests/resources/cow.png", "rb") as cow:
    ImageLoader().load_collection([mountain.read(), cow.read()])
# You can also use the load_files utility function
ImageLoader().load_collection(list(load_files(["tests/resources/mountain.png", "tests/resources/cow.png"]).values()))
```


## Email Loader

!!! info
    This driver requires the `loaders-email` [extra](../index.md#extras).

Can be used to load email from an imap server:

```python
from griptape.loaders import EmailLoader

loader = EmailLoader(imap_url="an.email.server.hostname", username="username", password="password")

loader.load(EmailLoader.EmailQuery(label="INBOX"))

loader.load_collection([EmailLoader.EmailQuery(label="INBOX"), EmailLoader.EmailQuery(label="SENT")])
```

## Audio Loader 

