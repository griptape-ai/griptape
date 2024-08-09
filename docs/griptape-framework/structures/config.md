---
search:
  boost: 2 
---

## Overview

The [DriverConfig](../../reference/griptape/config/driver_config.md) class allows for the customization of Structures within Griptape, enabling specific settings such as Drivers to be defined for Tasks. 

### Premade Configs

Griptape provides predefined [DriverConfig](../../reference/griptape/config/driver_config.md)'s for widely used services that provide APIs for most Driver types Griptape offers.

#### OpenAI

The [OpenAI Driver config](../../reference/griptape/config/openai_driver_config.md) provides default Drivers for OpenAI's APIs. This is the default config for all Structures.

```python
--8<-- "docs/griptape-framework/structures/src/config_1.py"
```

#### Azure OpenAI

The [Azure OpenAI Driver config](../../reference/griptape/config/azure_openai_driver_config.md) provides default Drivers for Azure's OpenAI APIs.

```python
--8<-- "docs/griptape-framework/structures/src/config_2.py"
```

#### Amazon Bedrock
The [Amazon Bedrock Driver config](../../reference/griptape/config/amazon_bedrock_driver_config.md) provides default Drivers for Amazon Bedrock's APIs.

```python
--8<-- "docs/griptape-framework/structures/src/config_3.py"
```

#### Google
The [Google Driver config](../../reference/griptape/config/google_driver_config.md) provides default Drivers for Google's Gemini APIs.

```python
--8<-- "docs/griptape-framework/structures/src/config_4.py"
```

#### Anthropic

The [Anthropic Driver config](../../reference/griptape/config/anthropic_driver_config.md) provides default Drivers for Anthropic's APIs.

!!! info
    Anthropic does not provide an embeddings API which means you will need to use another service for embeddings.
    The `AnthropicDriverConfig` defaults to using `VoyageAiEmbeddingDriver` which integrates with [VoyageAI](https://www.voyageai.com/), the service used in Anthropic's [embeddings documentation](https://docs.anthropic.com/claude/docs/embeddings).
    To override the default embedding driver, see: [Override Default Structure Embedding Driver](../drivers/embedding-drivers.md#override-default-structure-embedding-driver).

```python
--8<-- "docs/griptape-framework/structures/src/config_5.py"
```

#### Cohere

The [Cohere Driver config](../../reference/griptape/config/cohere_driver_config.md) provides default Drivers for Cohere's APIs.

```python
--8<-- "docs/griptape-framework/structures/src/config_6.py"
```

### Custom Configs

You can create your own [DriverConfig](../../reference/griptape/config/driver_config.md) by overriding relevant Drivers.
The [DriverConfig](../../reference/griptape/config/driver_config.md) class includes "Dummy" Drivers for all types, which throw a [DummyError](../../reference/griptape/exceptions/dummy_exception.md) if invoked without being overridden. 
This approach ensures that you are informed through clear error messages if you attempt to use Structures without proper Driver configurations.

```python
--8<-- "docs/griptape-framework/structures/src/config_7.py"
```

### Loading/Saving Configs

```python
--8<-- "docs/griptape-framework/structures/src/config_8.py"
```
