# Warpspeed

[![Tests](https://github.com/usewarpspeed/warpspeed/actions/workflows/tests.yml/badge.svg)](https://github.com/usewarpspeed/warpspeed/actions/workflows/tests.yml)
[![PyPI Version](https://img.shields.io/pypi/v/warpspeed.svg)](https://pypi.python.org/pypi/warpspeed)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/gitbucket/gitbucket/blob/master/LICENSE)
[![Twitter](https://img.shields.io/twitter/url/https/twitter.com/usewarpspeed.svg?style=social&label=Follow%20%40usewarpspeed)](https://twitter.com/usewarpspeed)

Warpspeed is a Python framework for creating AI workflow DAGs and pipelines. It augments transformer models with tools for accessing external APIs, such as searches, calculators, spreadsheets, docs, email, and many others. Our initial focus is on supporting large language models (LLMs) but we plan to expand framework's capabilities to cover text-to-anything functionality soon.

With Warpspeed, you can accomplish the following:

1. 🚰 Build sequential **AI pipelines** and sprawling **DAG workflows** for complex use cases.
2. 🧰️ Augment LLMs with **chain of thought** capabilities and **external tools**, such as calculators, web search, spreadsheet editors, and API connectors.
3. 💾 Add **memory** to AI pipelines for context preservation and summarization.

Please note that Warpspeed is in early development. Its APIs and documentation are subject to change. For now, this README file is the most accurate source of documentation and examples.

## Getting Started
First, install Warpspeed with `pip`:

```
pip install warpspeed
```

Second, configure an OpenAI client by [getting an API key](https://beta.openai.com/account/api-keys) and adding it to your environment as `OPENAI_API_KEY`. Warpspeed uses [OpenAI Completions API](https://platform.openai.com/docs/guides/completion) to execute LLM prompts and to work with [LlamaIndex](https://gpt-index.readthedocs.io/en/latest/index.html) data structures.

With Warpspeed, you can create *structures*, such as `Pipelines` and `Workflows`, that are composed of different types of steps. You can also define structures as JSON objects and load them into Warpspeed dynamically. Let's start with defining a simple pipeline.

## 🚰 AI Pipelines and Workflows

Pipelines are lists of steps that are executed sequentially. Pipelines can have `Memory`, which makes them ideal for storing LLM conversations.

```python
from warpspeed import utils
from warpspeed.memory import PipelineMemory
from warpspeed.steps import PromptStep
from warpspeed.structures import Pipeline

pipeline = Pipeline(
    memory=PipelineMemory()
)

pipeline.add_steps(
    PromptStep("{{ args[0] }}"),
    PromptStep("Say the following like a pirate: {{ input }}")
)

pipeline.run("I am Scotty, who are you?")
pipeline.run("Who am I?")

print(utils.Conversation(pipeline.memory).to_string())
```

Boom! Our first conversation, à la ChatGPT, is here:

> Q: I am Scotty, who are you?  
> A: Arrr, I be an AI language model designed to assist and answer yer questions, matey!  
> Q: Who am I?  
> A: Yarrr, ye just introduced yerself as Scotty, so ye be Scotty, matey!

You can dynamically pass arguments to the prompt by using Jinja templates:

```python
PromptStep("tell me about {{ topic }}", context={"topic": "the hobbit novel"})
```

In addition to user-defined fields, the `context` object contains the following:

### As Part of `Pipeline`
- `args`: arguments passed to the `Construct.run()` method.
- `input`: input from the parent.
- `structure`: the structure that the step belongs to.
- `parent`: parent step.
- `child`: child step.

### As Part of `Workflow`
- `args`: arguments passed to the `Construct.run()` method.
- `inputs`: inputs into the current step referencable by parent step IDs.
- `structure`: the structure that the step belongs to.
- `parents`: parent steps referencable by IDs.
- `children`: child steps referencable by IDs.

Warpspeed uses OpenAI's `gpt-3.5-turbo` model by default. If you want to use a different model, set a custom OpenAI prompt driver:

```python
Pipeline(
    prompt_driver=OpenAiPromptDriver(temperature=0.1, model="gpt-4")
)
```

Now, let's build a simple workflow. Let's say, we want to write a story in a fantasy world with some unique characters. We could setup a workflow that generates a world based on some keywords. Then we pass the world description to any number of child steps that create characters. Finally, the last step pulls in information from all parent steps and writes up a short story.

```python
def character_step(step_id, character_name) -> PromptStep:
    return PromptStep(
        "Based on the following world description create a character named {{ name }}:\n{{ inputs['world'] }}",
        context={
            "name": character_name
        },
        id=step_id
    )

world_step = PromptStep(
    "Create a fictional world based on the following key words {{ keywords|join(', ') }}",
    context={
        "keywords": ["fantasy", "ocean", "tidal lock"]
    },
    id="world"
)

character_step_1 = character_step("scotty", "Scotty")
character_step_2 = character_step("annie", "Annie")

story_step = PromptStep(
    "Based on the following description of the world and characters, write a short story:\n{{ inputs['world'] }}\n{{ inputs['scotty'] }}\n{{ inputs['annie'] }}",
    id="story"
)

workflow = Workflow()

workflow.add_step(world_step)

world_step.add_child(character_step_1)
world_step.add_child(character_step_2)
world_step.add_child(story_step)

character_step_1.add_child(story_step)
character_step_2.add_child(story_step)

workflow.run()

[print(step.output.value) for step in workflow.output_steps()]
```

And here is the beginning of our story:

> Scotty and Annie had been friends since childhood, and their bond had only grown stronger over the years. Scotty had always been fascinated by the ocean and its secrets, and Annie had always been drawn to its magical creatures. [...]

Workflows and pipelines can also be defined in JSON files and loaded dynamically in Python:

```json
{
  "prompt_driver": {
    "temperature": 0.5,
    "type": "OpenAiPromptDriver"
  },
  "steps": [
    {
      "id": "world",
      "type": "PromptStep",
      "parent_ids": [],
      "child_ids": [
        "scotty",
        "annie"
      ],
      "prompt_template": "Create a fictional world based on the following key words {{ keywords|join(', ') }}",
      "context": {
        "keywords": [
          "fantasy",
          "ocean",
          "tidal lock"
        ]
      }
    },
    ...
  ]
}
```

Here is how you can load and run it:

```python
with open("workflow.json", "r") as file:
    workflow = Workflow.from_json(file.read())

    workflow.run()
```

## 🧰️ Tools

The most powerful feature of Warpspeed is the ability of workflow and pipeline prompt steps to generate *chains of thought* and use tools that can interact with the outside world. We use the [ReAct](https://arxiv.org/abs/2210.03629) technique to implement reasoning and acting in the underlying LLMs without using any fine-tuning. There are two types of tool steps that Warpspeed supports:

- `ToolStep` takes one tool as a parameter and passes it to the LLM that decides if it should use it to respond to the prompt.
- `ToolkitStep` takes multiple tools as a parameter, so that the underlying LLM can decide which tool to use for every chain of thought step.

Here is how to use tools:

```python
pipeline = Pipeline()

pipeline.add_steps(
    ToolStep(
        "Research and summarize the most important events of February 2023",
        tool=WikiTool()
    ),
    ToolkitStep(
        "Calculate 3^12 and send an email with the answer and the following text to hello@warpspeed.cc:\n{{ input }}",
        tools=[
            CalculatorTool(),
            EmailSenderTool(
                host="localhost",
                port=1025,
                from_email="hello@warpspeed.cc",
                use_ssl=False
            )
        ],
        id="calc_email"
    )
)

pipeline.run()
```

`ToolStep` instructs an LLM to use a `WikiTool` that provides a JSON schema and *few-shot learning* examples that the LLM is automatically "trained" on to interact with Warpspeed. The LLM can then decide to use a tool to provide a better prompt response by adding substeps that follow the Thought/Action/Observation ReAct routine. For this prompt, it can obviously use a Wiki tool to obtain new information.

`ToolkitStep` works the same way, but it provides multiple tools for the LLM to choose from depending on the task. In our example, the LLM uses `CalculatorTool` to calculate `3^12` and `EmailSenderTool` to send an email.

Warpspeed supports multiple tools and allows you to implement your own.

### `AwsTool`

This tool enables LLMs to run AWS CLI commands. Before using this tool, make sure to [install and configure](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) AWS CLI v2.

```python
ToolStep(
    "show me all of my VPCs",
    tool=AwsTool()
)
```

> **Warning**
> By default, this tool uses `CommandRunner`, which executes commands locally in a subprocess. This is not ideal for production environments, where you generally want to execute arbitrary commands in a container. We are working on adding more command runner options soon.

### `CalculatorTool`

This tool enables LLMs to make simple calculations. Here's how to use it:

```python
ToolStep(
    "what's 123^321?",
    tool=CalculatorTool()
)
```

The LLM will be prompted to reason via the Thought/Action/Observation loop to use the calculator and respond with an answer that the calculator provided.

> **Warning**
> By default, this tool uses `PythonRunner`, which executes code locally with sanitized `exec`. This is not ideal for production environments, where you generally want to execute arbitrary code in a container. We are working on adding more code runner options soon.

### `SqlClientTool`

This tool enables LLMs to execute SQL statements via [SQLAlchemy](https://www.sqlalchemy.org/). Depending on your underlying SQL engine, [configure](https://docs.sqlalchemy.org/en/20/core/engines.html) your `engine_url` and give the LLM a hint about what engine you are using via `engine_hint`, so that it can create engine-specific statements.

```python
ToolStep(
    "list the last 20 items in the orders table",
    tool=SqlClientTool(
        engine_url="sqlite:///warpspeed.db",
        engine_hint="sqlite"
    )
)
```

### `DataScientistTool`

This tool enables LLMs to run more complex calculations in Python. The user can notify the LLM which libraries are available by specifying them in the constructor. By default, only `math` is available.

```python
ToolStep(
    "what's 123^321?",
    tool=DataScientistTool(
        libs={"numpy": "np", "math": "math"}
    )
)
```

This will make `numpy` available as `np` via `import numpy as np` and `math` as `math` via `import math`. Before injecting libraries in the constructor, make sure they are installed in your current environment.

> **Warning**
> By default, this tool uses `PythonRunner`, which executes code locally with sanitized `exec`. This is not ideal for production environments, where you generally want to execute arbitrary code in a container. We are working on adding more code runner options soon.

### `GoogleSearchTool`

This tool enables LLMs to search Google. Every search returns links, titles, and short descriptions. Search has two modes: scraping (default) and API-based. To enable [API-based search](https://programmablesearchengine.google.com) set `use_api`, `api_search_key`, and `api_search_id` params.

```python
ToolStep(
    "Find the latest on LLMs",
    tool=GoogleSearchTool()
)
```

### `GoogleSheetsWriterTool` and `GoogleSheetsReaderTool`

These tools enable LLMs to read from and write to Google Sheets worksheets. Before using those tools, make sure to download the service account credentials JSON file and share your spreadsheet with the service account. For more information refer to the `gspread` [auth docs](https://docs.gspread.org/en/latest/oauth2.html).

To read from a spreadsheet:

```python
ToolStep(
    "read all spreadsheet values from the 2nd and 3rd columns",
    tool=GoogleSheetsReaderTool(
        auth_key_path=os.path.expanduser("~/Desktop/service_account.json"),
        spreadsheet_key="<Google Sheets spreadsheet ID>",
        worksheet_name="<optional worksheet name, defaults to the first worksheet>"
    )
)
```

To write to a spreadsheet:

```python
ToolStep(
    "Create a spreadsheet with columns for 2022 months in the MM/YYYY format, last column for totals, and rows for profit, revenue, and loss",
    tool=GoogleSheetsWriterTool(
        auth_key_path=os.path.expanduser("~/Desktop/service_account.json"),
        spreadsheet_key="<Google Sheets spreadsheet ID>",
        worksheet_name="<optional worksheet name, defaults to the first worksheet>"
    )
)
```

### `EmailSenderTool`

This tool enables LLMs to send emails.

```python
ToolStep(
    "send an email with a haiku to hello@warpspeed.cc",
    EmailSenderTool(
        host="localhost",
        port=1025,
        from_email="hello@warpspeed.cc",
        use_ssl=False
    )
)
```

For debugging purposes, you can run a local SMTP server that the LLM will send emails to:

```shell
python -m smtpd -c DebuggingServer -n localhost:1025
```

User the `WARPSPEED_EMAIL_SENDER_TOOL_PASSWORD` environment variable to set the password.

### `WebScraperTool`

This tool enables LLMs to scrape web pages for full text, summaries, authors, titles, and keywords. It can also execute search queries to answer specific questions about the page.

```python
ToolStep(
    "Can you tell me what's on this page? https://github.com/usewarpspeed/warpspeed",
    tool=WebScraperTool()
)
```

### `WikiTool`

This tool enables LLMs to search and query Wikipedia articles:

```python
ToolStep(
    "Research and summarize biggest world news stories in February of 2023",
    tool=WikiTool()
)
```

### Building Your Own Tool

Building your own tools is easy with Warpspeed! All you need is a Python class, JSON schema to describe tool actions to the LLM, a set of examples, and a Marshmallow schema for serialization/deserialization. Let's walk through all the required steps and build a simple random number generator tool.

First, create a Python class in a separate directory that generates a random float and optionally truncates it:

```python
import random
from typing import Optional
from warpspeed.tools import Tool


class RandomGenTool(Tool):
    def run(self, num_of_decimals: Optional[int]) -> float:
        if num_of_decimals is None:
            return random.random()
        else:
            return round(random.random(), num_of_decimals)

```

Add a `schema.json` file describing the tool:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "random_gen",
  "description": "This tool can be used to generate random numbers",
  "type": "object",
  "properties": {
    "tool": {
      "type": "string",
      "enum": ["random_gen"]
    },
    "input": {
      "type": "int",
      "description": "The number of decimals to be considered while rounding. Default to null."
    }
  },
  "required": ["tool", "input"]
}
```

Finally, add an `examples.j2` Jinja file with a couple of few-shot learning examples:

```
Input: generate a random number
Thought: I need to use the random_gen tool to answer this question.
Action: {"tool": "random_gen", "input": null}
Observation: 0.8444218515250481
Thought: I have enough information to answer the question
Output: 0.8444218515250481

Input: generate a random number and round it to 2 decimal places
Thought: I need to use the random_gen tool to answer this question.
Action: {"tool": "random_gen", "input": 2}
Observation: 0.14
Thought: I have enough information to answer the question
Output: 0.14
```

Finally, if you want to use `to_json` and `from_json` serialization/deserialization methods, you'll have to add a [Marshmallow](https://marshmallow.readthedocs.io/en/stable/) schema to your tool:

```python
from marshmallow import post_load
from warpspeed.schemas import BaseSchema


class RandomGenToolSchema(BaseSchema):
    @post_load
    def make_obj(self, data, **kwargs):
        from .random_gen.random_gen_tool import RandomGenTool

        return RandomGenTool(**data)

```

The schema class has to be in the following format: `<ToolClassName>Schema` and be located in `<tool_class_name>_schema.py`.

Before using the tool, make sure to create an `__init__.py` file in the tool directory with the following contents:

```python
from .random_gen_tool import RandomGenTool
from .random_gen_tool_schema import RandomGenToolSchema

__all__ = [
    "RandomGenTool",
    "RandomGenToolSchema"
]

```

Finally, to use the tool:

```python
from warpspeed.steps import ToolStep
from random_gen.random_gen_tool import RandomGenTool


ToolStep(
    "generate a random number and round it to 3 decimal places",
    tool=RandomGenTool()
)
```

If you are deserializing a workflow or a pipeline from JSON, make sure to specify deserialization schema namespace:

```json
{
  "schema_namespace": "random_gen.random_gen_tool_schema",
  "type": "RandomGenTool"
}
```

Check out other [Warpspeed tools](https://github.com/usewarpspeed/warpspeed/tree/main/warpspeed/tools) to learn more about tools' implementation details. 

## 💾 Memory

Warpspeed supports different types of memory for pipelines. Due to the non-linear nature of workflows you can't use memory with them yet, but we are currently investigating other possibilities.

By default, pipelines don't initialize memory, so you have to explicitly pass it to them:

```python
Pipeline(
    memory=PipelineMemory()
)
```

There are two other types of memory: `BufferPipelineMemory` and `SummaryPipelineMemory`. `BufferPipelineMemory` will keep a sliding window of steps that are used to construct a prompt:

```python
Pipeline(
    memory=BufferPipelineMemory(buffer_size=3)
)
```

This works great for shorter pipelines but fails if the whole workflow context needs to be present. You can use `SummaryMemory` to address that:

```python
Pipeline(
    memory=SummaryPipelineMemory(
        summarizer=CompletionDriverSummarizer(
            driver=OpenAiPromptDriver()
        ),
        offset=2
    )
)
```

This will progressively summarize the whole pipeline except for the last two steps.

## Contributing

Contributions in the form of bug reports, feature ideas, or pull requests are super welcome! Take a look at the current issues and if you'd like to help please submit a pull request with some tests.

## License

Warpspeed is available under the Apache 2.0 License.