---
search:
  boost: 2 
---

## Overview

Griptape exposes global configuration options to easily customize different parts of the framework.

### Driver Configs

The [DriverConfig](../../reference/griptape/config/drivers/driver_config.md) class allows for the customization of Structures within Griptape, enabling specific settings such as Drivers to be defined for Tasks. 

Griptape provides predefined [DriverConfig](../../reference/griptape/config/drivers/driver_config.md)'s for widely used services that provide APIs for most Driver types Griptape offers.

#### OpenAI

The [OpenAI Driver config](../../reference/griptape/config/drivers/openai_driver_config.md) provides default Drivers for OpenAI's APIs. This is the default config for all Structures.

```python
--8<-- "docs/griptape-framework/structures/src/config_1.py"
```

#### Azure OpenAI

The [Azure OpenAI Driver config](../../reference/griptape/config/drivers/azure_openai_driver_config.md) provides default Drivers for Azure's OpenAI APIs.

```python
--8<-- "docs/griptape-framework/structures/src/config_2.py"
```

#### Amazon Bedrock
The [Amazon Bedrock Driver config](../../reference/griptape/config/drivers/amazon_bedrock_driver_config.md) provides default Drivers for Amazon Bedrock's APIs.

```python
--8<-- "docs/griptape-framework/structures/src/config_3.py"
```

#### Google
The [Google Driver config](../../reference/griptape/config/drivers/google_driver_config.md) provides default Drivers for Google's Gemini APIs.

```python
--8<-- "docs/griptape-framework/structures/src/config_4.py"
```

#### Anthropic

The [Anthropic Driver config](../../reference/griptape/config/drivers/anthropic_driver_config.md) provides default Drivers for Anthropic's APIs.

!!! info
    Anthropic does not provide an embeddings API which means you will need to use another service for embeddings.
    The `AnthropicDriverConfig` defaults to using `VoyageAiEmbeddingDriver` which integrates with [VoyageAI](https://www.voyageai.com/), the service used in Anthropic's [embeddings documentation](https://docs.anthropic.com/claude/docs/embeddings).
    To override the default embedding driver, see: [Override Default Structure Embedding Driver](../drivers/embedding-drivers.md#override-default-structure-embedding-driver).

```python
--8<-- "docs/griptape-framework/structures/src/config_5.py"
```

#### Cohere

The [Cohere Driver config](../../reference/griptape/config/drivers/cohere_driver_config.md) provides default Drivers for Cohere's APIs.

```python
--8<-- "docs/griptape-framework/structures/src/config_6.py"
```

#### Custom

You can create your own [DriverConfig](../../reference/griptape/config/drivers/driver_config.md) by overriding relevant Drivers.
The [DriverConfig](../../reference/griptape/config/drivers/driver_config.md) class includes "Dummy" Drivers for all types, which throw a [DummyError](../../reference/griptape/exceptions/dummy_exception.md) if invoked without being overridden. 
This approach ensures that you are informed through clear error messages if you attempt to use Structures without proper Driver configurations.

```python
--8<-- "docs/griptape-framework/structures/src/config_7.py"
```

### Logging Config

Griptape provides a predefined [LoggingConfig](../../reference/griptape/config/logging/logging_config.md)'s for easily customizing the logging events that the framework emits. In order to customize the logger, the logger can be fetched by using the `config.logging.logger_name`.

```python
--8<-- "docs/griptape-framework/structures/src/config_logging.py"
```

### Loading/Saving Configs

```python
--8<-- "docs/griptape-framework/structures/src/config_8.py"
```
