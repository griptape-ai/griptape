---
search:
  boost: 2 
---

## Overview

Griptape exposes global configuration options to easily customize different parts of the framework.

### Drivers Configs

The [DriversConfig](../../reference/griptape/configs/drivers/drivers_config.md) class allows for the customization of Structures within Griptape, enabling specific settings such as Drivers to be defined for Tasks. 

Griptape provides predefined [DriversConfig](../../reference/griptape/configs/drivers/drivers_config.md)'s for widely used services that provide APIs for most Driver types Griptape offers.

#### OpenAI

The [OpenAI Driver config](../../reference/griptape/configs/drivers/openai_drivers_config.md) provides default Drivers for OpenAI's APIs. This is the default config for all Structures.

```python
--8<-- "docs/griptape-framework/structures/src/drivers_config_1.py"
```

#### Azure OpenAI

The [Azure OpenAI Driver config](../../reference/griptape/configs/drivers/azure_openai_drivers_config.md) provides default Drivers for Azure's OpenAI APIs.

```python
--8<-- "docs/griptape-framework/structures/src/drivers_config_2.py"
```

#### Amazon Bedrock
The [Amazon Bedrock Driver config](../../reference/griptape/configs/drivers/amazon_bedrock_drivers_config.md) provides default Drivers for Amazon Bedrock's APIs.

```python
--8<-- "docs/griptape-framework/structures/src/drivers_config_3.py"
```

#### Google
The [Google Driver config](../../reference/griptape/configs/drivers/google_drivers_config.md) provides default Drivers for Google's Gemini APIs.

```python
--8<-- "docs/griptape-framework/structures/src/drivers_config_4.py"
```

#### Anthropic

The [Anthropic Driver config](../../reference/griptape/configs/drivers/anthropic_drivers_config.md) provides default Drivers for Anthropic's APIs.

!!! info
    Anthropic does not provide an embeddings API which means you will need to use another service for embeddings.
    The `AnthropicDriversConfig` defaults to using `VoyageAiEmbeddingDriver` which integrates with [VoyageAI](https://www.voyageai.com/), the service used in Anthropic's [embeddings documentation](https://docs.anthropic.com/claude/docs/embeddings).
    To override the default embedding driver, see: [Override Default Structure Embedding Driver](../drivers/embedding-drivers.md#override-default-structure-embedding-driver).

```python
--8<-- "docs/griptape-framework/structures/src/drivers_config_5.py"
```

#### Cohere

The [Cohere Driver config](../../reference/griptape/configs/drivers/cohere_drivers_config.md) provides default Drivers for Cohere's APIs.

```python
--8<-- "docs/griptape-framework/structures/src/drivers_config_6.py"
```

#### Custom

You can create your own [DriversConfig](../../reference/griptape/configs/drivers/drivers_config.md) by overriding relevant Drivers.
The [DriversConfig](../../reference/griptape/configs/drivers/drivers_config.md) class includes "Dummy" Drivers for all types, which throw a [DummyError](../../reference/griptape/exceptions/dummy_exception.md) if invoked without being overridden. 
This approach ensures that you are informed through clear error messages if you attempt to use Structures without proper Driver configurations.

```python
--8<-- "docs/griptape-framework/structures/src/drivers_config_7.py"
```

### Overriding Default Configs

While using a Default Driver Config, there may be instances in which you wish to override default drivers in order to mix and match LLM providers as needed. The following example showcases a Default of `OpenAiDriversConfig` with overrides for the `vector_store_driver`:

```python
import os

from griptape.configs import Defaults
from griptape.configs.drivers import OpenAiDriversConfig
from griptape.drivers import AstraDbVectorStoreDriver, OpenAiEmbeddingDriver
from griptape.loaders import WebLoader
from griptape.structures import Agent

# Astra DB secrets and connection parameters
api_endpoint = os.environ["ASTRA_DB_API_ENDPOINT"]
token = os.environ["ASTRA_DB_APPLICATION_TOKEN"]
astra_db_namespace = os.environ.get("ASTRA_DB_KEYSPACE")  # optional
TEST_COLLECTION_NAME = "gt_int_test"

embedding_driver = OpenAiEmbeddingDriver(api_key=os.environ["OPENAI_API_KEY"])
vector_store_driver = AstraDbVectorStoreDriver(
    embedding_driver=embedding_driver,
    api_endpoint=api_endpoint,
    token=token,
    collection_name=TEST_COLLECTION_NAME,
    astra_db_namespace=astra_db_namespace,  # optional
)
Defaults.drivers_config = OpenAiDriversConfig(
    embedding_driver=embedding_driver,
    vector_store_driver=vector_store_driver,
)

# This agent will be created with all the default drivers from the OpenAI drivers config,
# and an override for the vector_store_driver to use AstraDbVectorStoreDriver
openai_agent = Agent()

# Load Artifacts from the web
artifacts = WebLoader().load("https://www.griptape.ai")

# Upsert Artifacts into the Vector Store Driver
[vector_store_driver.upsert_text_artifact(a, namespace="griptape") for a in artifacts]

results = vector_store_driver.query(query="What is griptape?")

values = [r.to_artifact().value for r in results]

print("\n\n".join(values))
```

### Logging Config

Griptape provides a predefined [LoggingConfig](../../reference/griptape/configs/logging/logging_config.md)'s for easily customizing the logging events that the framework emits. In order to customize the logger, the logger can be fetched by using the `Defaults.logging.logger_name`.

```python
--8<-- "docs/griptape-framework/structures/src/logging_config.py"
```

### Loading/Saving Configs

```python
--8<-- "docs/griptape-framework/structures/src/drivers_config_8.py"
```
