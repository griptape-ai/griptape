---
search:
  boost: 2 
---

## Overview

Image Query Drivers are used by [Image Query Engines](../engines/image-query-engines.md) to execute natural language queries on the contents of images. You can specify the provider and model used to query the image by providing the Engine with a particular Image Query Driver.

!!! info
    All Image Query Drivers default to a `max_tokens` of 256. It is recommended that you set this value to correspond to the desired response length. 

## Image Query Drivers

### Anthropic

!!! info
    To tune `max_tokens`, see [Anthropic's documentation on image tokens](https://docs.anthropic.com/claude/docs/vision#image-costs) for more information on how to relate token count to response length.

The [AnthropicImageQueryDriver](../../reference/griptape/drivers/image_query/anthropic_image_query_driver.md) is used to query images using Anthropic's Claude 3 multi-modal model. Here is an example of how to use it:

```python
--8<-- "docs/griptape-framework/drivers/src/image_query_drivers_1.py"
```

You can also specify multiple images with a single text prompt. This applies the same text prompt to all images specified, up to a max of 20. However, you will still receive one text response from the model currently.

```python
--8<-- "docs/griptape-framework/drivers/src/image_query_drivers_2.py"
```

### OpenAI

!!! info
    While the `max_tokens` field is optional, it is recommended to set this to a value that corresponds to the desired response length. Without an explicit value, the model will default to very short responses. See [OpenAI's documentation](https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them) for more information on how to relate token count to response length.

The [OpenAiVisionImageQueryDriver](../../reference/griptape/drivers/image_query/openai_image_query_driver.md) is used to query images using the OpenAI Vision API. Here is an example of how to use it:

```python
--8<-- "docs/griptape-framework/drivers/src/image_query_drivers_3.py"
```

### Azure OpenAI
    
!!! info
    In order to use the `gpt-4-vision-preview` model on Azure OpenAI, the `gpt-4` model must be deployed with the version set to `vision-preview`. More information can be found in the [Azure OpenAI documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/gpt-with-vision).

The [AzureOpenAiVisionImageQueryDriver](../../reference/griptape/drivers/image_query/azure_openai_image_query_driver.md) is used to query images using the Azure OpenAI Vision API. Here is an example of how to use it:

```python
--8<-- "docs/griptape-framework/drivers/src/image_query_drivers_4.py"
```

### Amazon Bedrock

The [Amazon Bedrock Image Query Driver](../../reference/griptape/drivers/image_query/amazon_bedrock_image_query_driver.md) provides multi-model access to image query models hosted by Amazon Bedrock. This Driver manages API calls to the Bedrock API, while the specific Model Drivers below format the API requests and parse the responses.

#### Claude

The [BedrockClaudeImageQueryModelDriver](../../reference/griptape/drivers/image_query_model/bedrock_claude_image_query_model_driver.md) provides support for Claude models hosted by Bedrock.

```python
--8<-- "docs/griptape-framework/drivers/src/image_query_drivers_5.py"
```
