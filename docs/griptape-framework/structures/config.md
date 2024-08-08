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
from griptape.config import OpenAiDriverConfig, Config

Config.drivers = OpenAiDriverConfig()

agent = Agent()
```

#### Azure OpenAI

The [Azure OpenAI Driver Config](../../reference/griptape/config/azure_openai_driver_config.md) provides default Drivers for Azure's OpenAI APIs.

```python
import os
from griptape.structures import Agent
from griptape.config import AzureOpenAiDriverConfig, Config

Config.drivers = AzureOpenAiDriverConfig(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT_3"],
    api_key=os.environ["AZURE_OPENAI_API_KEY_3"]
)

agent = Agent()
```

#### Amazon Bedrock
The [Amazon Bedrock Driver Config](../../reference/griptape/config/amazon_bedrock_driver_config.md) provides default Drivers for Amazon Bedrock's APIs.

```python
import os
import boto3
from griptape.structures import Agent
from griptape.config import AmazonBedrockDriverConfig, Config

Config.drivers = AmazonBedrockDriverConfig(
    session=boto3.Session(
        region_name=os.environ["AWS_DEFAULT_REGION"],
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    )
)

agent = Agent()
```

#### Google
The [Google Driver Config](../../reference/griptape/config/google_driver_config.md) provides default Drivers for Google's Gemini APIs.

```python
from griptape.structures import Agent
from griptape.config import GoogleDriverConfig, Config

Config.drivers = GoogleDriverConfig()

agent = Agent()
```

#### Anthropic

The [Anthropic Driver Config](../../reference/griptape/config/anthropic_driver_config.md) provides default Drivers for Anthropic's APIs.

!!! info
    Anthropic does not provide an embeddings API which means you will need to use another service for embeddings.
    The `AnthropicDriverConfig` defaults to using `VoyageAiEmbeddingDriver` which integrates with [VoyageAI](https://www.voyageai.com/), the service used in Anthropic's [embeddings documentation](https://docs.anthropic.com/claude/docs/embeddings).
    To override the default embedding driver, see: [Override Default Structure Embedding Driver](../drivers/embedding-drivers.md#override-default-structure-embedding-driver).

```python
from griptape.structures import Agent
from griptape.config import AnthropicDriverConfig, Config

Config.drivers = AnthropicDriverConfig()

agent = Agent()
```

#### Cohere

The [Cohere Driver Config](../../reference/griptape/config/cohere_driver_config.md) provides default Drivers for Cohere's APIs.

```python
import os
from griptape.config import CohereDriverConfig, Config
from griptape.structures import Agent

Config.drivers = CohereDriverConfig(api_key=os.environ["COHERE_API_KEY"])

agent = Agent()
```

### Custom Configs

You can create your own [DriverConfig](../../reference/griptape/config/driver_config.md) by overriding relevant Drivers.
The [DriverConfig](../../reference/griptape/config/driver_config.md) class includes "Dummy" Drivers for all types, which throw a [DummyError](../../reference/griptape/exceptions/dummy_exception.md) if invoked without being overridden. 
This approach ensures that you are informed through clear error messages if you attempt to use Structures without proper Driver configurations.

```python
import os
from griptape.structures import Agent
from griptape.config import DriverConfig, Config
from griptape.drivers import AnthropicPromptDriver

Config.drivers = DriverConfig(
    prompt=AnthropicPromptDriver(
        model="claude-3-sonnet-20240229",
        api_key=os.environ["ANTHROPIC_API_KEY"],
    )
)


agent = Agent()
```

### Loading/Saving Configs

```python
from griptape.structures import Agent
from griptape.config import AmazonBedrockDriverConfig, Config

custom_config = AmazonBedrockDriverConfig()
dict_config = custom_config.to_dict()
# Use OpenAi for embeddings
dict_config["embedding"] = {
    "base_url": None,
    "model": "text-embedding-3-small",
    "organization": None,
    "type": "OpenAiEmbeddingDriver",
}
custom_config = AmazonBedrockDriverConfig.from_dict(dict_config)

Config.drivers = custom_config

agent = Agent()
```
