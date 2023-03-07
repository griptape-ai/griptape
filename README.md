# Warpspeed

[![Tests](https://github.com/usewarpspeed/warpspeed/actions/workflows/tests.yml/badge.svg)](https://github.com/usewarpspeed/warpspeed/actions/workflows/tests.yml)
[![PyPI Version](https://img.shields.io/pypi/v/warpspeed.svg)](https://pypi.python.org/pypi/warpspeed)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/gitbucket/gitbucket/blob/master/LICENSE)
[![Twitter](https://img.shields.io/twitter/url/https/twitter.com/usewarpspeed.svg?style=social&label=Follow%20%40usewarpspeed)](https://twitter.com/usewarpspeed)

Warpspeed is a Python framework for creating AI workflow DAGs and pipelines. It augments transformer models with tools for accessing external APIs, such as searches, calculators, spreadsheets, docs, email, and many others. Our initial focus is on supporting large language models (LLMs) but we plan to expand framework's capabilities to cover text-to-anything functionality soon.

With Warpspeed, you can accomplish the following:

1. 🚰 Build sequential **AI pipelines** and sprawling **DAG workflows** for complex use cases.
2. 🧰️ Augment LLMs with **chain of thought** capabilities and **external tools**, such as calculators, web search, spreadsheet editors, and API connectors.
3. 💾 Add **memory** to AI pipelines for context preservation.

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
pipeline = Pipeline(
    memory=Memory()
)

pipeline.add_steps(
    PromptStep("Hi, my name is Scotty. Who are you?"),
    PromptStep("What is my name?")
)

utils.Conversation(pipeline).to_string()
```

Boom! Our first conversation, à la ChatGPT, is here:

> Q: Hi, my name is Scotty. Who are you?  
> A: Hi Scotty, my name is Assistant. I'm here to help answer your questions.  
> Q: What is my name?  
> A: Your name is Scotty.

You can dynamically pass arguments to the prompt by using Jinja templates:

```python
PromptStep("tell me about {{ topic }}", context={"topic": "the hobbit novel"})
```

In addition to user-defined fields, the `context` object contains the following:
- `inputs`: inputs into the current step referencable by parent step IDs.
- `structure`: the structure that the step belongs to.
- `parents`: parent steps referencable by IDs.
- `chidlren`: child steps referencable by IDs.

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
        tool=WikiTool(),
        id="research"
    ),
    ToolkitStep(
        "Calculate 3^12 and send an email with the answer and the following text to hello@warpspeed.cc:\n{{ inputs['research'] }}",
        tools=[
            CalculatorTool(),
            EmailTool(
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

`ToolkitStep` works the same way, but it provides multiple tools for the LLM to choose from depending on the task. In our example, the LLM uses `CalculatorTool` to calculate `3^12` and `EmailTool` to send an email.

Warpspeed has the following tools:
- `CalculatorTool` for calculating simple algebraic expressions.
- `DataScientist` for answering more complex computational questions with `math` and `numpy` libraries.
- `EmailTool` for sending emails.
- `WikiTool` for searching and querying Wikipedia pages.

More tools to support spreadsheets, docs, web search, page scraping, and databases are coming soon.

## 💾 Memory

Warpspeed supports different types of memory for pipelines. Due to the complexities of the non-linear nature of workflows you can't use memory with them yet, and we are currently investigating other options.

By default, pipelines don't initialize memory, so you have to explicitly pass it to them:

```python
Pipeline(
    memory=Memory()
)
```

There are two other types of memory: `BufferMemory` and `SummaryMemory`. `BufferMemory` will keep a sliding window of steps that are used to construct a prompt:

```python
Pipeline(
    memory=BufferMemory(buffer_size=3)
)
```

This works great for shorter pipelines but fails if the whole workflow context needs to be present. You can use `SummaryMemory` to address that:

```python
Pipeline(
    memory=SummaryMemory(
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