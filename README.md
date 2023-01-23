# GalaxyBrain

[![PyPI Version](https://img.shields.io/pypi/v/galaxybrain.svg)](https://pypi.python.org/pypi/galaxybrain)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/gitbucket/gitbucket/blob/master/LICENSE)
[![Tests](https://github.com/galaxybrain-labs/galaxybrain/actions/workflows/tests.yml/badge.svg)](https://github.com/galaxybrain-labs/galaxybrain/actions/workflows/tests.yml)

_Turn LLMs into mighty shape rotators!_

GalaxyBrain is a workflow framework designed for large language models (LLMs). It allows developers to define prompt completion steps, prompt rules, result validators, and more. The framework also enhances LLM workflows by providing memory capabilities, enabling easy handling of state between steps.

Please note that GalaxyBrain is an experimental Python library in early development. Its APIs and documentation are subject to change. For usage examples, check out the [examples repository](https://github.com/galaxybrain-labs/galaxybrain-examples) which contains the most current examples of the library's usage.

## Goals

1. Reduce surprises when it comes to working with LLMs.
1. Focus on production LLM use cases and CI/CD compatibility.
1. Avoid bloat and keep base primitives simple.

## Getting Started
First, install the library:

```
pip install galaxybrain
```

Currently, GalaxyBrain only supports OpenAI APIs, so you'll need to [get an API key](https://beta.openai.com/account/api-keys) and keep it on your path as `OPENAI_API_KEY` or pass it to the driver object manually. For example:

```python
import os
from dotenv import load_dotenv
from galaxybrain.drivers import OpenAiCompletionDriver

load_dotenv()

driver = OpenAiCompletionDriver(os.environ.get('OPENAI_KEY'))
```


Here is an example of some of GalaxyBrain's functionality:

```python
from galaxybrain.rules import Rule, Validator
from galaxybrain.workflows import CompletionStep, Workflow
from galaxybrain.drivers import OpenAiCompletionDriver
from galaxybrain.prompts import Prompt
import galaxybrain.rules as rules

chat_rules = [
    rules.json.return_valid_json(),
    rules.json.put_answer_in_field("Names"),
    rules.meta.be_truthful(),
    rules.meta.your_name_is("GalaxyGPT"),
    Rule("only use information from fantasy novels")
]
driver = OpenAiCompletionDriver(temperature=0.5, user="demo")
workflow = Workflow(rules=chat_rules, completion_driver=driver)

workflow.add_step(
    CompletionStep(input=Prompt("Give me ideas for two names from the same universe"))
)

workflow.start()

# Output:
# {
#     "Names": ["Frodo Baggins", "Gandalf the Grey"]
# }

workflow.add_step(
    CompletionStep(input=Prompt("Give me 3 more from another universe"))
)

workflow.resume()

# Output:
# {
#     "Names": ["Dumbledore", "Luna Lovegood", "Harry Potter"]
# }
```

Use `ComputeStep` to delegate computational tasks to Python:

```python
ComputeStep(input=Prompt(f"generate two random 3x3 matrices and multiply them"))
```

This will generate the following code that GalaxyBrain runs locally and returns it to the LLM in the next prompt:

```python
print(np.matmul(np.random.rand(3,3), np.random.rand(3,3)))
```

You can also ask more open-ended computational questions:
```python
ComputeStep(input=Prompt(f"Sally is 5 feet tall, Jack is 14 inches taller than Sally. How tall is Jack?"))
```


You can also validate results against your rules:

```python
validator = Validator(workflow.last_step().output, chat_rules)

if validator.validate():
    print("Rule validations passed")
else:
    print("Rule validations failed")
    print(validator.failed_rules())
```