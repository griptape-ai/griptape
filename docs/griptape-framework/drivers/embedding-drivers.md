## Overview
Embeddings in Griptape are multidimensional representations of text data. Embeddings carry semantic information, which makes them useful for extracting relevant chunks from large bodies of text for search and querying.

Griptape provides a way to build Embedding Drivers that are reused in downstream framework components. Every Embedding Driver has two basic methods that can be used to generate embeddings:

* [embed_text_artifact()](../../reference/griptape/drivers/embedding/base_embedding_driver.md#griptape.drivers.embedding.base_embedding_driver.BaseEmbeddingDriver.embed_text_artifact) for [TextArtifact](../../reference/griptape/artifacts/text_artifact.md)s.
* [embed_string()](../../reference/griptape/drivers/embedding/base_embedding_driver.md#griptape.drivers.embedding.base_embedding_driver.BaseEmbeddingDriver.embed_string) for any string.

You can optionally provide a [Tokenizer](../misc/tokenizers.md) via the [tokenizer](../../reference/griptape/drivers/embedding/base_embedding_driver.md#griptape.drivers.embedding.base_embedding_driver.BaseEmbeddingDriver.tokenizer) field to have the Driver automatically chunk the input text to fit into the token limit.

## Embedding Drivers

### OpenAI Embeddings

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

### Azure OpenAI Embeddings

The [AzureOpenAiEmbeddingDriver](../../reference/griptape/drivers/embedding/azure_openai_embedding_driver.md) uses the same parameters as [OpenAiEmbeddingDriver](../../reference/griptape/drivers/embedding/openai_embedding_driver.md)
with updated defaults.

### Bedrock Titan Embeddings

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

### Google Embeddings
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

### Hugging Face Hub Embeddings

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
        max_output_tokens=512,
        tokenizer=AutoTokenizer.from_pretrained(
            "sentence-transformers/all-MiniLM-L6-v2"
        )
    ),
)

embeddings = driver.embed_string("Hello world!")

# display the first 3 embeddings
print(embeddings[:3])
```
### Multi Model Embedding Drivers
Certain embeddings providers such as Amazon SageMaker support many types of models, each with their own slight differences in parameters and response formats. To support this variation across models, these Embedding Drivers takes a [Embedding Model Driver](../../reference/griptape/drivers/embedding_model/base_embedding_model_driver.md)
through the [embedding_model_driver](../../reference/griptape/drivers/embedding/base_multi_model_embedding_driver.md#griptape.drivers.embedding.base_multi_model_embedding_driver.BaseMultiModelEmbeddingDriver.embedding_model_driver) parameter.
[Embedding Model Driver](../../reference/griptape/drivers/embedding_model/base_embedding_model_driver.md)s allows for model-specific customization for Embedding Drivers. 

#### SageMaker Embeddings

The [AmazonSageMakerEmbeddingDriver](../../reference/griptape/drivers/embedding/amazon_sagemaker_embedding_driver.md) uses the [Amazon SageMaker Endpoints](https://docs.aws.amazon.com/sagemaker/latest/dg/realtime-endpoints.html) to generate embeddings on AWS.

!!! info
    This driver requires the `drivers-embedding-amazon-sagemaker` [extra](../index.md#extras).

##### TensorFlow Hub Models
```python title="PYTEST_IGNORE"
import os
from griptape.drivers import AmazonSageMakerEmbeddingDriver, SageMakerTensorFlowHubEmbeddingModelDriver

driver = AmazonSageMakerEmbeddingDriver(
    model=os.environ["SAGEMAKER_TENSORFLOW_HUB_MODEL"],
    embedding_model_driver=SageMakerTensorFlowHubEmbeddingModelDriver(),
)

embeddings = driver.embed_string("Hello world!")

# display the first 3 embeddings
print(embeddings[:3])
```

##### HuggingFace Models
```python title="PYTEST_IGNORE"
import os
from griptape.drivers import AmazonSageMakerEmbeddingDriver, SageMakerHuggingFaceEmbeddingModelDriver

driver = AmazonSageMakerEmbeddingDriver(
    model=os.environ["SAGEMAKER_HUGGINGFACE_MODEL"],
    embedding_model_driver=SageMakerHuggingFaceEmbeddingModelDriver(),
)

embeddings = driver.embed_string("Hello world!")

# display the first 3 embeddings
print(embeddings[:3])
```

### VoyageAI Embeddings
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
