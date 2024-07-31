---
search:
  boost: 2 
---

## Overview

The [StructureConfig](../../reference/griptape/config/structure_config.md) class allows for the customization of Structures within Griptape, enabling specific settings such as Drivers to be defined for Tasks. 

### Premade Configs

Griptape provides predefined [StructureConfig](../../reference/griptape/config/structure_config.md)'s for widely used services that provide APIs for most Driver types Griptape offers.

#### OpenAI

The [OpenAI Structure Config](../../reference/griptape/config/openai_structure_config.md) provides default Drivers for OpenAI's APIs. This is the default config for all Structures.


```python
from griptape.structures import Agent
from griptape.config import OpenAiStructureConfig

agent = Agent(
    config=OpenAiStructureConfig()
)

agent = Agent() # This is equivalent to the above
```

#### Azure OpenAI

The [Azure OpenAI Structure Config](../../reference/griptape/config/azure_openai_structure_config.md) provides default Drivers for Azure's OpenAI APIs.


```python
import os
from griptape.structures import Agent
from griptape.config import AzureOpenAiStructureConfig

agent = Agent(
    config=AzureOpenAiStructureConfig(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT_3"],
        api_key=os.environ["AZURE_OPENAI_API_KEY_3"]
    )
)
```

#### Amazon Bedrock
The [Amazon Bedrock Structure Config](../../reference/griptape/config/amazon_bedrock_structure_config.md) provides default Drivers for Amazon Bedrock's APIs.

```python
import os
import boto3
from griptape.structures import Agent
from griptape.config import AmazonBedrockStructureConfig

agent = Agent(
    config=AmazonBedrockStructureConfig(
        session=boto3.Session(
            region_name=os.environ["AWS_DEFAULT_REGION"],
            aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        )
    )
)
```

#### Google
The [Google Structure Config](../../reference/griptape/config/google_structure_config.md) provides default Drivers for Google's Gemini APIs.

```python
from griptape.structures import Agent
from griptape.config import GoogleStructureConfig

agent = Agent(
    config=GoogleStructureConfig()
)
```

#### Anthropic

The [Anthropic Structure Config](../../reference/griptape/config/anthropic_structure_config.md) provides default Drivers for Anthropic's APIs.

!!! info
    Anthropic does not provide an embeddings API which means you will need to use another service for embeddings.
    The `AnthropicStructureConfig` defaults to using `VoyageAiEmbeddingDriver` which integrates with [VoyageAI](https://www.voyageai.com/), the service used in Anthropic's [embeddings documentation](https://docs.anthropic.com/claude/docs/embeddings).
    To override the default embedding driver, see: [Override Default Structure Embedding Driver](../drivers/embedding-drivers.md#override-default-structure-embedding-driver).


```python
from griptape.structures import Agent
from griptape.config import AnthropicStructureConfig

agent = Agent(
    config=AnthropicStructureConfig()
)
```

#### Cohere

The [Cohere Structure Config](../../reference/griptape/config/cohere_structure_config.md) provides default Drivers for Cohere's APIs.


```python
import os
from griptape.config import CohereStructureConfig
from griptape.structures import Agent

agent = Agent(config=CohereStructureConfig(api_key=os.environ["COHERE_API_KEY"]))
```

### Custom Configs

You can create your own [StructureConfig](../../reference/griptape/config/structure_config.md) by overriding relevant Drivers.
The [StructureConfig](../../reference/griptape/config/structure_config.md) class includes "Dummy" Drivers for all types, which throw a [DummyError](../../reference/griptape/exceptions/dummy_exception.md) if invoked without being overridden. 
This approach ensures that you are informed through clear error messages if you attempt to use Structures without proper Driver configurations.

```python
import os
from griptape.structures import Agent
from griptape.config import StructureConfig
from griptape.drivers import AnthropicPromptDriver

agent = Agent(
    config=StructureConfig(
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
from griptape.config import AmazonBedrockStructureConfig
from griptape.drivers import AmazonBedrockCohereEmbeddingDriver

custom_config = AmazonBedrockStructureConfig()
custom_config.embedding_driver = AmazonBedrockCohereEmbeddingDriver()
custom_config.merge_config(
    {
        "embedding_driver": {
            "base_url": None,
            "model": "text-embedding-3-small",
            "organization": None,
            "type": "OpenAiEmbeddingDriver",
        },
    }
)
serialized_config = custom_config.to_json()
deserialized_config = AmazonBedrockStructureConfig.from_json(serialized_config)

agent = Agent(
    config=deserialized_config.merge_config({
        "prompt_driver" : {
            "model": "anthropic.claude-3-sonnet-20240229-v1:0",
        },
    }),
)
```

