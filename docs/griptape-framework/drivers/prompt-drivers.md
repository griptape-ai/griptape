## Overview

Prompt Drivers are used by Griptape Structures to make API calls to the underlying LLMs. [OpenAi Chat](#openai-chat) is the default prompt driver used in all structures.

You can instantiate drivers and pass them to structures:

```python
from griptape.structures import Agent
from griptape.drivers import OpenAiChatPromptDriver
from griptape.rules import Rule
from griptape.config import StructureConfig

agent = Agent(
    config=StructureConfig(
        prompt_driver=OpenAiChatPromptDriver(model="gpt-4o", temperature=0.3),
    ),
    input_template="You will be provided with a tweet, and your task is to classify its sentiment as positive, neutral, or negative. Tweet: {{ args[0] }}",
    rules=[
        Rule(
            value="Output only the sentiment."
        )
    ],
)

agent.run("I loved the new Batman movie!")
```

Or use them independently:

```python
from griptape.utils import PromptStack
from griptape.drivers import OpenAiChatPromptDriver

stack = PromptStack()

stack.add_system_input(
    "You will be provided with Python code, and your task is to calculate its time complexity."
)
stack.add_user_input(
"""
def foo(n, k):
    accum = 0
    for i in range(n):
        for l in range(k):
            accum += i
    return accum
"""
)

result = OpenAiChatPromptDriver(model="gpt-3.5-turbo-16k", temperature=0).run(stack)

print(result.value)
```

## Prompt Drivers

Griptape offers the following Prompt Drivers for interacting with LLMs.

!!! warning
    When overriding a default Prompt Driver, take care to ensure you've updated the Structure's configured Embedding Driver as well. If Task Memory isn't needed, you can avoid compatability issues by setting `task_memory=None` to disable Task Memory in your Structure.

### OpenAI Chat

The [OpenAiChatPromptDriver](../../reference/griptape/drivers/prompt/openai_chat_prompt_driver.md) connects to the [OpenAI Chat](https://platform.openai.com/docs/guides/chat) API.

```python
import os
from griptape.structures import Agent
from griptape.drivers import OpenAiChatPromptDriver
from griptape.rules import Rule
from griptape.config import StructureConfig

agent = Agent(
    config=StructureConfig(
        prompt_driver=OpenAiChatPromptDriver(
            api_key=os.environ["OPENAI_API_KEY"],
            temperature=0.1,
            model="gpt-4o",
            response_format="json_object",
            seed=42,
        )
    ),
    input_template="You will be provided with a description of a mood, and your task is to generate the CSS code for a color that matches it. Description: {{ args[0] }}",
    rules=[
        Rule(
            value='Write your output in json with a single key called "css_code".'
        )
    ],
)

agent.run("Blue sky at dusk.")
```

!!! info
    `response_format` and `seed` are unique to the OpenAI Chat Prompt Driver and Azure OpenAi Chat Prompt Driver.

### Azure OpenAI Chat

The [AzureOpenAiChatPromptDriver](../../reference/griptape/drivers/prompt/azure_openai_chat_prompt_driver.md) connects to Azure OpenAI [Chat Completion](https://learn.microsoft.com/en-us/azure/cognitive-services/openai/reference) APIs.

```python
import os
from griptape.structures import Agent
from griptape.rules import Rule
from griptape.drivers import AzureOpenAiChatPromptDriver
from griptape.config import StructureConfig

agent = Agent(
    config=StructureConfig(
        prompt_driver=AzureOpenAiChatPromptDriver(
            api_key=os.environ["AZURE_OPENAI_API_KEY_1"],
            model="gpt-3.5-turbo-16k",
            azure_deployment=os.environ["AZURE_OPENAI_35_TURBO_16K_DEPLOYMENT_ID"],
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT_1"],
        )
    ),
    rules=[
        Rule(
            value="You will be provided with text, and your task is to translate it into emojis. "
                  "Do not use any regular text. Do your best with emojis only."
        )
    ],
)

agent.run("Artificial intelligence is a technology with great promise.")
```

### Cohere

The [CoherePromptDriver](../../reference/griptape/drivers/prompt/cohere_prompt_driver.md) connects to the Cohere [Generate](https://docs.cohere.ai/reference/generate) API.

!!! info
    This driver requires the `drivers-prompt-cohere` [extra](../index.md#extras).

```python
import os
from griptape.structures import Agent
from griptape.drivers import CoherePromptDriver
from griptape.config import StructureConfig

agent = Agent(
    config=StructureConfig(
        prompt_driver=CoherePromptDriver(
            model="command",
            api_key=os.environ['COHERE_API_KEY'],
        )
    )
)

agent.run('What is the sentiment of this review? Review: "I really enjoyed this movie!"')
```

### Anthropic

!!! info
    This driver requires the `drivers-prompt-anthropic` [extra](../index.md#extras).

The [AnthropicPromptDriver](../../reference/griptape/drivers/prompt/anthropic_prompt_driver.md) connects to the Anthropic [Messages](https://docs.anthropic.com/claude/reference/messages_post) API.

```python
import os
from griptape.structures import Agent
from griptape.drivers import AnthropicPromptDriver
from griptape.config import StructureConfig

agent = Agent(
    config=StructureConfig(
        prompt_driver=AnthropicPromptDriver(
            model="claude-3-opus-20240229",
            api_key=os.environ['ANTHROPIC_API_KEY'],
        )
    )
)

agent.run('Where is the best place to see cherry blossums in Japan?')
```

### Google

!!! info
    This driver requires the `drivers-prompt-google` [extra](../index.md#extras).

The [GooglePromptDriver](../../reference/griptape/drivers/prompt/google_prompt_driver.md) connects to the [Google Generative AI](https://ai.google.dev/tutorials/python_quickstart#generate_text_from_text_inputs) API.

```python
import os
from griptape.structures import Agent
from griptape.drivers import GooglePromptDriver
from griptape.config import StructureConfig

agent = Agent(
    config=StructureConfig(
        prompt_driver=GooglePromptDriver(
            model="gemini-pro",
            api_key=os.environ['GOOGLE_API_KEY'],
        )
    )
)

agent.run('Briefly explain how a computer works to a young child.')
```

### Amazon Bedrock

!!! info
    This driver requires the `drivers-prompt-amazon-bedrock` [extra](../index.md#extras).

The [AmazonBedrockPromptDriver](../../reference/griptape/drivers/prompt/amazon_bedrock_prompt_driver.md) uses [Amazon Bedrock](https://aws.amazon.com/bedrock/)'s [Converse API](https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html).

All models supported by the Converse API are available for use with this driver.

```python
from griptape.structures import Agent
from griptape.drivers import AmazonBedrockPromptDriver
from griptape.rules import Rule
from griptape.config import StructureConfig

agent = Agent(
    config=StructureConfig(
        prompt_driver=AmazonBedrockPromptDriver(
            model="anthropic.claude-3-sonnet-20240229-v1:0",
        )
    ),
    rules=[
        Rule(
            value="You are a customer service agent that is classifying emails by type. I want you to give your answer and then explain it."
        )
    ],
)
agent.run(
    """How would you categorize this email?
    <email>
    Can I use my Mixmaster 4000 to mix paint, or is it only meant for mixing food?
    </email>

    Categories are:
    (A) Pre-sale question
    (B) Broken or defective item
    (C) Billing question
    (D) Other (please explain)"""
)
```

### Ollama

!!! info
    This driver requires the `drivers-prompt-ollama` [extra](../index.md#extras).

The [OllamaPromptDriver](../../reference/griptape/drivers/prompt/ollama_prompt_driver.md) connects to the [Ollama Chat Completion API](https://github.com/ollama/ollama/blob/main/docs/api.md#generate-a-chat-completion).

```python
from griptape.config import StructureConfig
from griptape.drivers import OllamaPromptDriver
from griptape.structures import Agent


agent = Agent(
    config=StructureConfig(
        prompt_driver=OllamaPromptDriver(
            model="llama3",
        ),
    ),
)
agent.run("What color is the sky at different times of the day?")
```

### Hugging Face Hub

!!! info
    This driver requires the `drivers-prompt-huggingface` [extra](../index.md#extras).

The [HuggingFaceHubPromptDriver](../../reference/griptape/drivers/prompt/huggingface_hub_prompt_driver.md) connects to the [Hugging Face Hub API](https://huggingface.co/docs/hub/api).


!!! warning
    Not all models featured on the Hugging Face Hub are supported by this driver. Models that are not supported by
    [Hugging Face serverless inference](https://huggingface.co/docs/api-inference/en/index) will not work with this driver.
    Due to the limitations of Hugging Face serverless inference, only models that are than 10GB are supported.

```python
import os
from griptape.structures import Agent
from griptape.drivers import HuggingFaceHubPromptDriver
from griptape.rules import Rule, Ruleset
from griptape.config import StructureConfig


agent = Agent(
    config=StructureConfig(
        prompt_driver=HuggingFaceHubPromptDriver(
            model="HuggingFaceH4/zephyr-7b-beta",
            api_token=os.environ["HUGGINGFACE_HUB_ACCESS_TOKEN"],
        )
    ),
    rulesets=[
        Ruleset(
            name="Girafatron",
            rules=[
                Rule(
                    value="You are Girafatron, a giraffe-obsessed robot. You are talking to a human. "
                    "Girafatron is obsessed with giraffes, the most glorious animal on the face of this Earth. "
                    "Giraftron believes all other animals are irrelevant when compared to the glorious majesty of the giraffe."
                )
            ],
        )
    ],
)

agent.run("Hello Girafatron, what is your favorite animal?")
```

#### Text Generation Interface

The [HuggingFaceHubPromptDriver](#hugging-face-hub) also supports [Text Generation Interface](https://huggingface.co/docs/text-generation-inference/basic_tutorials/consuming_tgi#inference-client) for running models locally. To use Text Generation Interface, just set `model` to a TGI endpoint.

```python title="PYTEST_IGNORE"
import os
from griptape.structures import Agent
from griptape.drivers import HuggingFaceHubPromptDriver
from griptape.config import StructureConfig


agent = Agent(
    config=StructureConfig(
        prompt_driver=HuggingFaceHubPromptDriver(
            model="http://127.0.0.1:8080",
            api_token=os.environ["HUGGINGFACE_HUB_ACCESS_TOKEN"],
        ),
    ),
)

agent.run("Write the code for a snake game.")
```

### Hugging Face Pipeline

!!! info
    This driver requires the `drivers-prompt-huggingface-pipeline` [extra](../index.md#extras).

The [HuggingFacePipelinePromptDriver](../../reference/griptape/drivers/prompt/huggingface_pipeline_prompt_driver.md) uses [Hugging Face Pipelines](https://huggingface.co/docs/transformers/main_classes/pipelines) for inference locally.

!!! warning
    Running a model locally can be a computationally expensive process.

```python
from griptape.structures import Agent
from griptape.drivers import HuggingFacePipelinePromptDriver
from griptape.rules import Rule, Ruleset
from griptape.config import StructureConfig


agent = Agent(
    config=StructureConfig(
        prompt_driver=HuggingFacePipelinePromptDriver(
            model="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        )
    ),
    rulesets=[
        Ruleset(
            name="Pirate",
            rules=[
                Rule(
                    value="You are a pirate chatbot who always responds in pirate speak!"
                )
            ],
        )
    ],
)

agent.run("How many helicopters can a human eat in one sitting?")
```

### Amazon SageMaker Jumpstart

!!! info
    This driver requires the `drivers-prompt-amazon-sagemaker` [extra](../index.md#extras).

The [AmazonSageMakerJumpstartPromptDriver](../../reference/griptape/drivers/prompt/amazon_sagemaker_jumpstart_prompt_driver.md) uses [Amazon SageMaker Jumpstart](https://docs.aws.amazon.com/sagemaker/latest/dg/studio-jumpstart.html) for inference on AWS.

Amazon Sagemaker Jumpstart provides a wide range of models with varying capabilities.
This Driver has been primarily _chat-optimized_ models that have a [Huggingface Chat Template](https://huggingface.co/docs/transformers/en/chat_templating) available.
If your model does not fit this use-case, we suggest sub-classing [AmazonSageMakerJumpstartPromptDriver](../../reference/griptape/drivers/prompt/amazon_sagemaker_jumpstart_prompt_driver.md) and overriding the `_to_model_input` and `_to_model_params` methods.
    

```python title="PYTEST_IGNORE"
import os
from griptape.structures import Agent
from griptape.drivers import (
    AmazonSageMakerJumpstartPromptDriver,
    SageMakerFalconPromptModelDriver,
)
from griptape.config import StructureConfig

agent = Agent(
    config=StructureConfig(
        prompt_driver=AmazonSageMakerJumpstartPromptDriver(
            endpoint=os.environ["SAGEMAKER_LLAMA_3_INSTRUCT_ENDPOINT_NAME"],
            model="meta-llama/Meta-Llama-3-8B-Instruct",
        )
    )
)

agent.run("What is a good lasagna recipe?")
```
