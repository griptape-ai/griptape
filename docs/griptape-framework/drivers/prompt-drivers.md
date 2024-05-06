## Overview

Prompt Drivers are used by Griptape Structures to make API calls to the underlying LLMs. [OpenAi Chat](#openai-chat) is the default prompt driver used in all structures.

You can instantiate drivers and pass them to structures:

```python
from griptape.structures import Agent
from griptape.drivers import OpenAiChatPromptDriver
from griptape.rules import Rule
from griptape.config import StructureConfig, StructureGlobalDriversConfig

agent = Agent(
    config=StructureConfig(
        global_drivers=StructureGlobalDriversConfig(
            prompt_driver=OpenAiChatPromptDriver(model="gpt-4", temperature=0.3),
        )
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
from griptape.config import StructureConfig, StructureGlobalDriversConfig

agent = Agent(
    config=StructureConfig(
        global_drivers=StructureGlobalDriversConfig(
            prompt_driver=OpenAiChatPromptDriver(
                api_key=os.environ["OPENAI_API_KEY"],
                temperature=0.1,
                model="gpt-3.5-turbo",
                response_format="json_object",
                seed=42,
            )
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
from griptape.config import StructureConfig, StructureGlobalDriversConfig

agent = Agent(
    config=StructureConfig(
        global_drivers=StructureGlobalDriversConfig(
            prompt_driver=AzureOpenAiChatPromptDriver(
                api_key=os.environ["AZURE_OPENAI_API_KEY_1"],
                model="gpt-3.5-turbo-16k",
                azure_deployment=os.environ["AZURE_OPENAI_35_TURBO_16K_DEPLOYMENT_ID"],
                azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT_1"],
            )
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

### Azure OpenAI Completion

The [AzureOpenAiCompletionPromptDriver](../../reference/griptape/drivers/prompt/azure_openai_completion_prompt_driver.md) connects to Azure OpenAI [Text Completion](https://learn.microsoft.com/en-us/azure/cognitive-services/openai/reference) API.

```python
import os
from griptape.structures import Agent
from griptape.drivers import AzureOpenAiCompletionPromptDriver
from griptape.config import StructureConfig, StructureGlobalDriversConfig

agent = Agent(
    config=StructureConfig(
        global_drivers=StructureGlobalDriversConfig(
            prompt_driver=AzureOpenAiCompletionPromptDriver(
                api_key=os.environ["AZURE_OPENAI_API_KEY_1"],
                model="text-davinci-003",
                azure_deployment=os.environ["AZURE_OPENAI_DAVINCI_DEPLOYMENT_ID"],
                azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT_1"],
                temperature=1
            )
        )
    )
)

agent.run(
    """
    Write a product launch email for new AI-powered headphones that are priced at $79.99 and available at Best Buy, Target and Amazon.com. The target audience is tech-savvy music lovers and the tone is friendly and exciting.

    1. What should be the subject line of the email?
    2. What should be the body of the email?
    """
)
```

### Cohere

The [CoherePromptDriver](../../reference/griptape/drivers/prompt/cohere_prompt_driver.md) connects to the Cohere [Generate](https://docs.cohere.ai/reference/generate) API.

!!! info
    This driver requires the `drivers-prompt-cohere` [extra](../index.md#extras).

```python
import os
from griptape.structures import Agent
from griptape.drivers import CoherePromptDriver
from griptape.config import StructureConfig, StructureGlobalDriversConfig

agent = Agent(
    config=StructureConfig(
        global_drivers=StructureGlobalDriversConfig(
            prompt_driver=CoherePromptDriver(
                model="command",
                api_key=os.environ['COHERE_API_KEY'],
            )
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
from griptape.config import StructureConfig, StructureGlobalDriversConfig

agent = Agent(
    config=StructureConfig(
        global_drivers=StructureGlobalDriversConfig(
            prompt_driver=AnthropicPromptDriver(
                model="claude-3-opus-20240229",
                api_key=os.environ['ANTHROPIC_API_KEY'],
            )
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
from griptape.config import StructureConfig, StructureGlobalDriversConfig

agent = Agent(
    config=StructureConfig(
        global_drivers=StructureGlobalDriversConfig(
            prompt_driver=GooglePromptDriver(
                model="gemini-pro",
                api_key=os.environ['GOOGLE_API_KEY'],
            )
        )
    )
)

agent.run('Briefly explain how a computer works to a young child.')
```

### Hugging Face Hub

!!! info
    This driver requires the `drivers-prompt-huggingface` [extra](../index.md#extras).

The [HuggingFaceHubPromptDriver](../../reference/griptape/drivers/prompt/huggingface_hub_prompt_driver.md) connects to the [Hugging Face Hub API](https://huggingface.co/docs/hub/api). It supports models with the following tasks:

- text2text-generation
- text-generation

Let's recreate the [Falcon-7B-Instruct](https://huggingface.co/tiiuae/falcon-7b-instruct) example using Griptape:

```python
import os
from griptape.structures import Agent
from griptape.drivers import HuggingFaceHubPromptDriver
from griptape.rules import Rule, Ruleset
from griptape.utils import PromptStack
from griptape.config import StructureConfig, StructureGlobalDriversConfig


def prompt_stack_to_string_converter(prompt_stack: PromptStack) -> str:
    prompt_lines = []

    for i in prompt_stack.inputs:
        if i.is_user():
            prompt_lines.append(f"User: {i.content}")
        elif i.is_assistant():
            prompt_lines.append(f"Girafatron: {i.content}")
        else:
            prompt_lines.append(f"Instructions: {i.content}")
    prompt_lines.append("Girafatron:")

    return "\n".join(prompt_lines)


agent = Agent(
    config=StructureConfig(
        global_drivers=StructureGlobalDriversConfig(
            prompt_driver=HuggingFaceHubPromptDriver(
                model="tiiuae/falcon-7b-instruct",
                api_token=os.environ["HUGGINGFACE_HUB_ACCESS_TOKEN"],
                prompt_stack_to_string=prompt_stack_to_string_converter,
            )
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
            ]
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
from griptape.config import StructureConfig, StructureGlobalDriversConfig


agent = Agent(
    config=StructureConfig(
        global_drivers=StructureGlobalDriversConfig(
            prompt_driver=HuggingFaceHubPromptDriver(
                model="http://127.0.0.1:8080",
                api_token=os.environ["HUGGINGFACE_HUB_ACCESS_TOKEN"],
            ),
        )
    ),
)

agent.run("Write the code for a snake game.")
```

### Hugging Face Pipeline

!!! info
    This driver requires the `drivers-prompt-huggingface` [extra](../index.md#extras).

The [HuggingFaceHubPromptDriver](../../reference/griptape/drivers/prompt/huggingface_pipeline_prompt_driver.md) uses [Hugging Face Pipelines](https://huggingface.co/docs/transformers/main_classes/pipelines) for inference locally. It supports models with the following tasks:

- text2text-generation
- text-generation

!!! warning
    Running a model locally can be a computationally expensive process.

```python
import os
from griptape.structures import Agent
from griptape.drivers import HuggingFaceHubPromptDriver
from griptape.rules import Rule, Ruleset
from griptape.utils import PromptStack
from griptape.config import StructureConfig, StructureGlobalDriversConfig


# Override the default Prompt Stack to string converter
# to format the prompt in a way that is easier for this model to understand.
def prompt_stack_to_string_converter(prompt_stack: PromptStack) -> str:
    prompt_lines = []

    for i in prompt_stack.inputs:
        if i.is_user():
            prompt_lines.append(f"User: {i.content}")
        elif i.is_assistant():
            prompt_lines.append(f"Girafatron: {i.content}")
        else:
            prompt_lines.append(f"Instructions: {i.content}")
    prompt_lines.append("Girafatron:")

    return "\n".join(prompt_lines)


agent = Agent(
    config=StructureConfig(
        global_drivers=StructureGlobalDriversConfig(
            prompt_driver=HuggingFaceHubPromptDriver(
                model="tiiuae/falcon-7b-instruct",
                api_token=os.environ["HUGGINGFACE_HUB_ACCESS_TOKEN"],
                prompt_stack_to_string=prompt_stack_to_string_converter,
            ),
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
            ]
        )
    ],
)

agent.run("Hello Girafatron, what is your favorite animal?")
```

### Multi Model Prompt Drivers
Certain LLM providers such as Amazon SageMaker and Amazon Bedrock supports many types of models, each with their own slight differences in prompt structure and parameters. To support this variation across models, these Prompt Drivers takes a [Prompt Model Driver](../../reference/griptape/drivers/prompt_model/base_prompt_model_driver.md)
through the [prompt_model_driver](../../reference/griptape/drivers/prompt/base_multi_model_prompt_driver.md#griptape.drivers.prompt.base_multi_model_prompt_driver.BaseMultiModelPromptDriver.prompt_model_driver) parameter.
[Prompt Model Driver](../../reference/griptape/drivers/prompt_model/base_prompt_model_driver.md)s allows for model-specific customization for Prompt Drivers. 


#### Amazon SageMaker

!!! info
    This driver requires the `drivers-prompt-amazon-sagemaker` [extra](../index.md#extras).

The [AmazonSageMakerPromptDriver](../../reference/griptape/drivers/prompt/amazon_sagemaker_prompt_driver.md) uses [Amazon SageMaker Endpoints](https://docs.aws.amazon.com/sagemaker/latest/dg/realtime-endpoints.html) for inference on AWS.

##### LLaMA

```python title="PYTEST_IGNORE"
import os
from griptape.structures import Agent
from griptape.drivers import (
    AmazonSageMakerPromptDriver,
    SageMakerLlamaPromptModelDriver,
)
from griptape.rules import Rule
from griptape.config import StructureConfig, StructureGlobalDriversConfig

agent = Agent(
    config=StructureConfig(
        global_drivers=StructureGlobalDriversConfig(
            prompt_driver=AmazonSageMakerPromptDriver(
                model=os.environ["SAGEMAKER_LLAMA_ENDPOINT_NAME"],
                prompt_model_driver=SageMakerLlamaPromptModelDriver(),
                temperature=0.75,
            ),
        )
    ),
    rules=[
        Rule(
            value="You are a helpful, respectful and honest assistant who is also a swarthy pirate."
            "You only speak like a pirate and you never break character."
        )
    ],
)

agent.run("Hello!")
```

##### Falcon

```python title="PYTEST_IGNORE"
import os
from griptape.structures import Agent
from griptape.drivers import (
    AmazonSageMakerPromptDriver,
    SageMakerFalconPromptModelDriver,
)
from griptape.config import StructureConfig, StructureGlobalDriversConfig

agent = Agent(
    config=StructureConfig(
        global_drivers=StructureGlobalDriversConfig(
            prompt_driver=AmazonSageMakerPromptDriver(
                model=os.environ["SAGEMAKER_FALCON_ENDPOINT_NAME"],
                prompt_model_driver=SageMakerFalconPromptModelDriver(),
            ),
        )
    )
)

agent.run("What is a good lasagna recipe?")

```

#### Amazon Bedrock

!!! info
    This driver requires the `drivers-prompt-amazon-bedrock` [extra](../index.md#extras).

The [AmazonBedrockPromptDriver](../../reference/griptape/drivers/prompt/amazon_bedrock_prompt_driver.md) uses [Amazon Bedrock](https://aws.amazon.com/bedrock/) for inference on AWS.

##### Amazon Titan

To use this model with Amazon Bedrock, use the [BedrockTitanPromptModelDriver](../../reference/griptape/drivers/prompt_model/bedrock_titan_prompt_model_driver.md).

```python
from griptape.structures import Agent
from griptape.drivers import AmazonBedrockPromptDriver, BedrockTitanPromptModelDriver
from griptape.config import StructureConfig, StructureGlobalDriversConfig

agent = Agent(
    config=StructureConfig(
        global_drivers=StructureGlobalDriversConfig(
            prompt_driver=AmazonBedrockPromptDriver(
                model="amazon.titan-text-express-v1",
                prompt_model_driver=BedrockTitanPromptModelDriver(
                    top_p=1,
                )
            )
        )
    )
)
agent.run(
    "Write an informational article for children about how birds fly."
    "Compare how birds fly to how airplanes fly."
    'Make sure to use the word "Thrust" at least three times.'
)
```

##### Anthropic Claude

To use this model with Amazon Bedrock, use the [BedrockClaudePromptModelDriver](../../reference/griptape/drivers/prompt_model/bedrock_claude_prompt_model_driver.md).

```python
from griptape.structures import Agent
from griptape.drivers import AmazonBedrockPromptDriver, BedrockClaudePromptModelDriver
from griptape.rules import Rule
from griptape.config import StructureConfig, StructureGlobalDriversConfig

agent = Agent(
    config=StructureConfig(
        global_drivers=StructureGlobalDriversConfig(
            prompt_driver=AmazonBedrockPromptDriver(
                model="anthropic.claude-3-sonnet-20240229-v1:0",
                prompt_model_driver=BedrockClaudePromptModelDriver(
                    top_p=1,
                ),
            ),
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
##### Meta Llama 2

To use this model with Amazon Bedrock, use the [BedrockLlamaPromptModelDriver](../../reference/griptape/drivers/prompt_model/bedrock_llama_prompt_model_driver.md).

```python
from griptape.structures import Agent
from griptape.drivers import AmazonBedrockPromptDriver, BedrockLlamaPromptModelDriver
from griptape.config import StructureConfig, StructureGlobalDriversConfig

agent = Agent(
    config=StructureConfig(
        global_drivers=StructureGlobalDriversConfig(
            prompt_driver=AmazonBedrockPromptDriver(
                model="meta.llama2-13b-chat-v1",
                prompt_model_driver=BedrockLlamaPromptModelDriver(),
            ),
        )
    )
)
agent.run(
    "Write an article about impact of high inflation to GDP of a country"
)
```

##### Ai21 Jurassic

To use this model with Amazon Bedrock, use the [BedrockJurassicPromptModelDriver](../../reference/griptape/drivers/prompt_model/bedrock_jurassic_prompt_model_driver.md).

```python
from griptape.structures import Agent
from griptape.drivers import AmazonBedrockPromptDriver, BedrockJurassicPromptModelDriver
from griptape.config import StructureConfig, StructureGlobalDriversConfig

agent = Agent(
    config=StructureConfig(
        global_drivers=StructureGlobalDriversConfig(
            prompt_driver=AmazonBedrockPromptDriver(
                model="ai21.j2-ultra-v1",
                prompt_model_driver=BedrockJurassicPromptModelDriver(top_p=0.95),
                temperature=0.7,
            )
        )
    )
)
agent.run(
    "Suggest an outline for a blog post based on a title. "
    "Title: How I put the pro in prompt engineering."
)
```
