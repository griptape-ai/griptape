## Overview
Embeddings in Griptape are multidimensional representations of text data. Embeddings carry semantic information, which makes them useful for extracting relevant chunks from large bodies of text for search and querying.

Griptape provides a way to build Embedding Drivers that are reused in downstream framework components. Every Embedding Driver has two basic methods that can be used to generate embeddings:

* [embed_text_artifact()](../../reference/griptape/drivers/embedding/base_embedding_driver.md#griptape.drivers.embedding.base_embedding_driver.BaseEmbeddingDriver.embed_text_artifact) for [TextArtifact](../../reference/griptape/artifacts/text_artifact.md)s.
* [embed_string()](../../reference/griptape/drivers/embedding/base_embedding_driver.md#griptape.drivers.embedding.base_embedding_driver.BaseEmbeddingDriver.embed_string) for any string.

You can optionally provide a [Tokenizer](../misc/tokenizers.md) via the [tokenizer](../../reference/griptape/drivers/embedding/base_embedding_driver.md#griptape.drivers.embedding.base_embedding_driver.BaseEmbeddingDriver.tokenizer) field to have the Driver automatically chunk the input text to fit into the token limit.

## Embedding Drivers

### OpenAI

The [OpenAiEmbeddingDriver](../../reference/griptape/drivers/embedding/openai_embedding_driver.md) uses the [OpenAI Embeddings API](https://platform.openai.com/docs/guides/embeddings).


```python
from griptape.drivers import OpenAiEmbeddingDriver

embeddings = OpenAiEmbeddingDriver().embed_string("Hello Griptape!")

# display the first 3 embeddings
print(embeddings[:3])
```
```
[0.0017853748286142945, 0.006118456833064556, -0.005811543669551611]
```

### Azure OpenAI

The [AzureOpenAiEmbeddingDriver](../../reference/griptape/drivers/embedding/azure_openai_embedding_driver.md) uses the same parameters as [OpenAiEmbeddingDriver](../../reference/griptape/drivers/embedding/openai_embedding_driver.md)
with updated defaults.

### Bedrock Titan

!!! info
    This driver requires the `drivers-embedding-amazon-bedrock` [extra](../index.md#extras).

The [AmazonBedrockTitanEmbeddingDriver](../../reference/griptape/drivers/embedding/amazon_bedrock_titan_embedding_driver.md) uses the [Amazon Bedrock Embeddings API](https://docs.aws.amazon.com/bedrock/latest/userguide/embeddings.html).

```python
from griptape.drivers import AmazonBedrockTitanEmbeddingDriver

embeddings = AmazonBedrockTitanEmbeddingDriver().embed_string("Hello world!")

# display the first 3 embeddings
print(embeddings[:3])
```
```
[-0.234375, -0.024902344, -0.14941406]
```

### Google
!!! info
    This driver requires the `drivers-embedding-google` [extra](../index.md#extras).

The [GoogleEmbeddingDriver](../../reference/griptape/drivers/embedding/google_embedding_driver.md) uses the [Google Embeddings API](https://ai.google.dev/tutorials/python_quickstart#use_embeddings).

```python
from griptape.drivers import GoogleEmbeddingDriver

embeddings = GoogleEmbeddingDriver().embed_string("Hello world!")

# display the first 3 embeddings
print(embeddings[:3])
```
```
[0.0588633, 0.0033929371, -0.072810836]
```

### Hugging Face Hub

!!! info
    This driver requires the `drivers-embedding-huggingface` [extra](../index.md#extras).

The [HuggingFaceHubEmbeddingDriver](../../reference/griptape/drivers/embedding/huggingface_hub_embedding_driver.md) connects to the [Hugging Face Hub API](https://huggingface.co/docs/hub/api). It supports models with the following tasks:

- feature-extraction

```python
import os
from griptape.drivers import HuggingFaceHubEmbeddingDriver
from griptape.tokenizers import HuggingFaceTokenizer
from transformers import AutoTokenizer

driver = HuggingFaceHubEmbeddingDriver(
    api_token=os.environ["HUGGINGFACE_HUB_ACCESS_TOKEN"],
    model="sentence-transformers/all-MiniLM-L6-v2",
    tokenizer=HuggingFaceTokenizer(
        model="sentence-transformers/all-MiniLM-L6-v2",
        max_output_tokens=512,
    ),
)

embeddings = driver.embed_string("Hello world!")

# display the first 3 embeddings
print(embeddings[:3])

```
### Amazon SageMaker Jumpstart

The [AmazonSageMakerJumpstartEmbeddingDriver](../../reference/griptape/drivers/embedding/amazon_sagemaker_jumpstart_embedding_driver.md) uses the [Amazon SageMaker Endpoints](https://docs.aws.amazon.com/sagemaker/latest/dg/realtime-endpoints.html) to generate embeddings on AWS.

!!! info
    This driver requires the `drivers-embedding-amazon-sagemaker` [extra](../index.md#extras).

```python title="PYTEST_IGNORE"
import os
from griptape.drivers import AmazonSageMakerJumpstartEmbeddingDriver, SageMakerTensorFlowHubEmbeddingModelDriver

driver = AmazonSageMakerJumpstartEmbeddingDriver(
    model=os.environ["SAGEMAKER_TENSORFLOW_HUB_MODEL"],
)

embeddings = driver.embed_string("Hello world!")

# display the first 3 embeddings
print(embeddings[:3])
```

### VoyageAI
The [VoyageAiEmbeddingDriver](../../reference/griptape/drivers/embedding/voyageai_embedding_driver.md) uses the [VoyageAI Embeddings API](https://www.voyageai.com/).

!!! info
    This driver requires the `drivers-embedding-voyageai` [extra](../index.md#extras).

```python
import os
from griptape.drivers import VoyageAiEmbeddingDriver

driver = VoyageAiEmbeddingDriver(
    api_key=os.environ["VOYAGE_API_KEY"]
)

embeddings = driver.embed_string("Hello world!")

# display the first 3 embeddings
print(embeddings[:3])
```

### Cohere

The [CohereEmbeddingDriver](../../reference/griptape/drivers/embedding/cohere_embedding_driver.md) uses the [Cohere Embeddings API](https://docs.cohere.com/docs/embeddings).

!!! info
    This driver requires the `drivers-embedding-cohere` [extra](../index.md#extras).

```python
import os
from griptape.drivers import CohereEmbeddingDriver

embedding_driver=CohereEmbeddingDriver(
    model="embed-english-v3.0",
    api_key=os.environ["COHERE_API_KEY"],
    input_type="search_document",
)

embeddings = embedding_driver.embed_string("Hello world!")

# display the first 3 embeddings
print(embeddings[:3])
```

### Override Default Structure Embedding Driver
Here is how you can override the Embedding Driver that is used by default in Structures. 

```python
from griptape.structures import Agent
from griptape.tools import WebScraper, TaskMemoryClient
from griptape.drivers import (
    OpenAiChatPromptDriver,
    VoyageAiEmbeddingDriver,
)
from griptape.config import StructureConfig

agent = Agent(
    tools=[WebScraper(off_prompt=True), TaskMemoryClient(off_prompt=False)],
    config=StructureConfig(
        prompt_driver=OpenAiChatPromptDriver(model="gpt-4o"),
        embedding_driver=VoyageAiEmbeddingDriver(),
    ),
)

agent.run("based on https://www.griptape.ai/, tell me what Griptape is")
```
