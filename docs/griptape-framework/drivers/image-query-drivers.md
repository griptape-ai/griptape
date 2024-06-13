# Image Query Drivers

Image Query Drivers are used by [Image Query Engines](../engines/query-engines.md#image) to execute natural language queries on the contents of images. You can specify the provider and model used to query the image by providing the Engine with a particular Image Query Driver.

!!! info
    All Image Query Drivers default to a `max_tokens` of 256. It is recommended that you set this value to correspond to the desired response length. 

## Anthropic

!!! info
    To tune `max_tokens`, see [Anthropic's documentation on image tokens](https://docs.anthropic.com/claude/docs/vision#image-costs) for more information on how to relate token count to response length.

The [AnthropicImageQueryDriver](../../reference/griptape/drivers/image_query/anthropic_image_query_driver.md) is used to query images using Anthropic's Claude 3 multi-modal model. Here is an example of how to use it:

```python
from griptape.drivers import AnthropicImageQueryDriver
from griptape.engines import ImageQueryEngine
from griptape.loaders import ImageLoader

driver = AnthropicImageQueryDriver(
    model="claude-3-sonnet-20240229",
    max_tokens=1024,
)

engine = ImageQueryEngine(
    image_query_driver=driver,
)

with open("tests/resources/mountain.png", "rb") as f:
    image_artifact = ImageLoader().load(f.read())

engine.run("Describe the weather in the image", [image_artifact])
```

You can also specify multiple images with a single text prompt. This applies the same text prompt to all images specified, up to a max of 20. However, you will still receive one text response from the model currently.

```python
from griptape.drivers import AnthropicImageQueryDriver
from griptape.engines import ImageQueryEngine
from griptape.loaders import ImageLoader

driver = AnthropicImageQueryDriver(
    model="claude-3-sonnet-20240229",
    max_tokens=1024,
)

engine = ImageQueryEngine(
    image_query_driver=driver,
)

with open("tests/resources/mountain.png", "rb") as f:
    image_artifact1 = ImageLoader().load(f.read())

with open("tests/resources/cow.png", "rb") as f:
    image_artifact2 = ImageLoader().load(f.read())

result = engine.run("Describe the weather in the image", [image_artifact1, image_artifact2])

print(result)
```

## OpenAI

!!! info
    While the `max_tokens` field is optional, it is recommended to set this to a value that corresponds to the desired response length. Without an explicit value, the model will default to very short responses. See [OpenAI's documentation](https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them) for more information on how to relate token count to response length.

The [OpenAiVisionImageQueryDriver](../../reference/griptape/drivers/image_query/openai_image_query_driver.md) is used to query images using the OpenAI Vision API. Here is an example of how to use it:

```python
from griptape.drivers import OpenAiImageQueryDriver
from griptape.engines import ImageQueryEngine
from griptape.loaders import ImageLoader

driver = OpenAiImageQueryDriver(
    model="gpt-4o",
    max_tokens=256,
)

engine = ImageQueryEngine(
    image_query_driver=driver,
)

with open("tests/resources/mountain.png", "rb") as f:
    image_artifact = ImageLoader().load(f.read())

engine.run("Describe the weather in the image", [image_artifact])
```

## Azure OpenAI
    
!!! info
    In order to use the `gpt-4-vision-preview` model on Azure OpenAI, the `gpt-4` model must be deployed with the version set to `vision-preview`. More information can be found in the [Azure OpenAI documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/gpt-with-vision).

The [AzureOpenAiVisionImageQueryDriver](../../reference/griptape/drivers/image_query/azure_openai_image_query_driver.md) is used to query images using the Azure OpenAI Vision API. Here is an example of how to use it:

```python
import os
from griptape.drivers import AzureOpenAiImageQueryDriver
from griptape.engines import ImageQueryEngine
from griptape.loaders import ImageLoader

driver = AzureOpenAiImageQueryDriver(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT_2"],
    api_key=os.environ["AZURE_OPENAI_API_KEY_2"],
    model="gpt-4o",
    azure_deployment="gpt-4o",
    max_tokens=256,
)

engine = ImageQueryEngine(
    image_query_driver=driver,
)

with open("tests/resources/mountain.png", "rb") as f:
    image_artifact = ImageLoader().load(f.read())

engine.run("Describe the weather in the image", [image_artifact])
```

## Amazon Bedrock

The [Amazon Bedrock Image Query Driver](../../reference/griptape/drivers/image_query/amazon_bedrock_image_query_driver.md) provides multi-model access to image query models hosted by Amazon Bedrock. This Driver manages API calls to the Bedrock API, while the specific Model Drivers below format the API requests and parse the responses.

### Claude

The [BedrockClaudeImageQueryModelDriver](../../reference/griptape/drivers/image_query_model/bedrock_claude_image_query_model_driver.md) provides support for Claude models hosted by Bedrock.

```python
from griptape.drivers import AmazonBedrockImageQueryDriver, BedrockClaudeImageQueryModelDriver
from griptape.engines import ImageQueryEngine
from griptape.loaders import ImageLoader
import boto3

session = boto3.Session(
    region_name="us-west-2"
)

driver = AmazonBedrockImageQueryDriver(
    image_query_model_driver=BedrockClaudeImageQueryModelDriver(),
    model="anthropic.claude-3-sonnet-20240229-v1:0",
    session=session
)

engine = ImageQueryEngine(
    image_query_driver=driver
)

with open("tests/resources/mountain.png", "rb") as f:
    image_artifact = ImageLoader().load(f.read())


result = engine.run("Describe the weather in the image", [image_artifact])

print(result)
```
