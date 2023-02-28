# GalaxyBrain

[![Tests](https://github.com/galaxybrain-labs/galaxybrain/actions/workflows/tests.yml/badge.svg)](https://github.com/galaxybrain-labs/galaxybrain/actions/workflows/tests.yml)
[![PyPI Version](https://img.shields.io/pypi/v/galaxybrain.svg)](https://pypi.python.org/pypi/galaxybrain)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/gitbucket/gitbucket/blob/master/LICENSE)
[![Twitter](https://img.shields.io/twitter/url/https/twitter.com/GetGalaxyBrain.svg?style=social&label=Follow%20%40GetGalaxyBrain)](https://twitter.com/GetGalaxyBrain)

_Turn LLMs into mighty shape rotators!_

GalaxyBrain is a Python framework for creating AI workflows augmented with tools for external APIs such as searches, calculators, email, and many others . Initially, we focus on supporting large language models (LLMs) starting with OpenAI's GPT. With GalaxyBrain, developers can define workflow steps, tools, LLM rules, result validators, and more. The framework also enhances LLM workflows by providing memory capabilities, enabling easy handling of state between steps.

Please note that GalaxyBrain is an experimental project in early development. Its APIs and documentation are subject to change. For usage examples, check out the [examples repository](https://github.com/galaxybrain-labs/galaxybrain-examples).

## Getting Started
First, install the library:

```
pip install galaxybrain
```

Currently, GalaxyBrain only supports OpenAI APIs, so you'll need to [get an API key](https://beta.openai.com/account/api-keys) and keep it on your path as `OPENAI_API_KEY` or pass it to the driver object manually. For example:

```python
import os
from dotenv import load_dotenv
from galaxybrain.drivers import OpenAiPromptDriver

load_dotenv()

driver = OpenAiPromptDriver(os.environ.get('OPENAI_KEY'))
```

## Working with GalaxyBrain

So...what can you do with GalaxyBrain?

### 📋 Define and Validate Prompt Rules

You can define rules that will be passed to the language model in the prompt stack:

```python
chat_rules = [
    rules.json.return_valid_json(),
    rules.json.put_answer_in_field("Names"),
    rules.meta.be_truthful(),
    rules.meta.your_name_is("GalaxyGPT"),
    Rule("only use information from fantasy novels")
]
driver = OpenAiPromptDriver(temperature=0.5, user="demo")
workflow = Workflow(rules=chat_rules, prompt_driver=driver)

workflow.add_step(
    PromptStep("Give me ideas for two names from the same setting")
)

workflow.start()

# {
#     "Names": ["Frodo Baggins", "Gandalf the Grey"]
# }

workflow.add_step(
    PromptStep("Give me 3 more from another setting")
)

workflow.resume()

# {
#     "Names": ["Dumbledore", "Luna Lovegood", "Harry Potter"]
# }
```

You can dynamically pass arguments to the prompt by using Jinja templates:

```python
PromptStep("tell me about {{ topic }}", context={"topic": "the hobbit novel"})
```

By default, the context object contains the following fields: `worklofw`, `input`, `parent`, and `child`.

Some rules have explicit validators (e.g., checking for valid JSON). You can use the built-in validator to run them:

```python
validator = Validator(workflow.last_step().output, chat_rules)

if validator.validate():
    print("Rule validations passed")
else:
    print("Rule validations failed")
    print(validator.failed_rules())
```

### ⚙️ Use Tools

Use `ToolStep` to pass external tools to the LLM:

```python
tools = {
    Wiki(),
    DataScientist(),
    Calculator(),
    Email(host="localhost", port=1025, from_email="my@email.com", password="", use_ssl=False)
}

workflow.add_steps(
    ToolStep("generate a random 4x4 matrix"),
    ToolStep("Research world events in 2023 and send an executive summary to me@email.com")
)
```

GalaxyBrain uses the [ReAct](https://arxiv.org/abs/2210.03629) technique to implement reasoning and acting in LLMs.

### 💾 Memorize and Summarize Workflows

GalaxyBrain `Workflow` uses unbounded memory by default, but you can pass `BufferMemory` or `SummaryMemory` to it explicitly:

```python
workflow = Workflow(
    prompt_driver=OpenAiPromptDriver(),
    memory=BufferMemory(buffer_size=1)
)
```

`BufferMemory` will keep a sliding window of steps that are used to construct a prompt. This works great for shorter conversations but falls short if the whole workflow context needs to be present. Use `SummaryMemory` to address that:

```python
driver = OpenAiPromptDriver()
workflow = Workflow(
    prompt_driver=driver,
    memory=SummaryMemory(
        summarizer=CompletionDriverSummarizer(driver=driver),
        offset=3
    )
)
```

This will progressively summarize the whole conversation except for the latest three steps.

## Contributing

Contributions in the form of bug reports, feature ideas, or pull requests are super welcome! Take a look at the current issues and if you'd like to help please submit a pull request with some tests.

## License

GalaxyBrain is available under the Apache 2.0 License.