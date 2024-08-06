---
search:
  boost: 2 
---

## Overview

The [DriverConfig](../../reference/griptape/config/driver_config.md) class allows for the customization of Structures within Griptape, enabling specific settings such as Drivers to be defined for Tasks. 

### Premade Configs

Griptape provides predefined [DriverConfig](../../reference/griptape/config/driver_config.md)'s for widely used services that provide APIs for most Driver types Griptape offers.

#### OpenAI

The [OpenAI Driver Config](../../reference/griptape/config/openai_driver_config.md) provides default Drivers for OpenAI's APIs. This is the default config for all Structures.

```python
from griptape.structures import Agent
from griptape.config import OpenAiDriverConfig

agent = Agent(
    config=OpenAiDriverConfig()
)

agent = Agent()  # This is equivalent to the above
```

#### Azure OpenAI

The [Azure OpenAI Driver Config](../../reference/griptape/config/azure_openai_driver_config.md) provides default Drivers for Azure's OpenAI APIs.

```python
import os
from griptape.structures import Agent
from griptape.config import AzureOpenAiDriverConfig

agent = Agent(
    config=AzureOpenAiDriverConfig(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT_3"],
        api_key=os.environ["AZURE_OPENAI_API_KEY_3"]
    ).merge_config({
        "image_query": {
            "azure_deployment": "gpt-4o",
        },
    }),
)
```

#### Amazon Bedrock
The [Amazon Bedrock Driver Config](../../reference/griptape/config/amazon_bedrock_driver_config.md) provides default Drivers for Amazon Bedrock's APIs.

```python
import os
import boto3
from griptape.structures import Agent
from griptape.config import AmazonBedrockDriverConfig

agent = Agent(
    config=AmazonBedrockDriverConfig(
        session=boto3.Session(
            region_name=os.environ["AWS_DEFAULT_REGION"],
            aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        )
    )
)
```

#### Google
The [Google Driver Config](../../reference/griptape/config/google_driver_config.md) provides default Drivers for Google's Gemini APIs.

```python
from griptape.structures import Agent
from griptape.config import GoogleDriverConfig

agent = Agent(
    config=GoogleDriverConfig()
)
```

#### Anthropic

The [Anthropic Driver Config](../../reference/griptape/config/anthropic_driver_config.md) provides default Drivers for Anthropic's APIs.

!!! info
    Anthropic does not provide an embeddings API which means you will need to use another service for embeddings.
    The `AnthropicDriverConfig` defaults to using `VoyageAiEmbeddingDriver` which integrates with [VoyageAI](https://www.voyageai.com/), the service used in Anthropic's [embeddings documentation](https://docs.anthropic.com/claude/docs/embeddings).
    To override the default embedding driver, see: [Override Default Structure Embedding Driver](../drivers/embedding-drivers.md#override-default-structure-embedding-driver).

```python
from griptape.structures import Agent
from griptape.config import AnthropicDriverConfig

agent = Agent(
    config=AnthropicDriverConfig()
)
```

#### Cohere

The [Cohere Driver Config](../../reference/griptape/config/cohere_driver_config.md) provides default Drivers for Cohere's APIs.

```python
import os
from griptape.config import CohereDriverConfig
from griptape.structures import Agent

agent = Agent(config=CohereDriverConfig(api_key=os.environ["COHERE_API_KEY"]))
```

### Custom Configs

You can create your own [DriverConfig](../../reference/griptape/config/driver_config.md) by overriding relevant Drivers.
The [DriverConfig](../../reference/griptape/config/driver_config.md) class includes "Dummy" Drivers for all types, which throw a [DummyError](../../reference/griptape/exceptions/dummy_exception.md) if invoked without being overridden. 
This approach ensures that you are informed through clear error messages if you attempt to use Structures without proper Driver configurations.

```python
import os
from griptape.structures import Agent
from griptape.config import DriverConfig
from griptape.drivers import AnthropicPromptDriver

agent = Agent(
    config=DriverConfig(
        prompt_driver=AnthropicPromptDriver(
            model="claude-3-sonnet-20240229",
            api_key=os.environ["ANTHROPIC_API_KEY"],
        )
    ),
)
```

### Loading/Saving Configs

Configuration classes in Griptape offer utility methods for loading, saving, and merging configurations, streamlining the management of complex setups.

```python
from griptape.structures import Agent
from griptape.config import AmazonBedrockDriverConfig
from griptape.drivers import AmazonBedrockCohereEmbeddingDriver

custom_config = AmazonBedrockDriverConfig()
custom_config.embedding_driver = AmazonBedrockCohereEmbeddingDriver()
custom_config.merge_config(
    {
        "embedding": {
            "base_url": None,
            "model": "text-embedding-3-small",
            "organization": None,
            "type": "OpenAiEmbeddingDriver",
        },
    }
)
serialized_config = custom_config.to_json()
deserialized_config = AmazonBedrockDriverConfig.from_json(serialized_config)

agent = Agent(
    config=deserialized_config.merge_config({
        "prompt": {
            "model": "anthropic.claude-3-sonnet-20240229-v1:0",
        },
    }),
)
```

