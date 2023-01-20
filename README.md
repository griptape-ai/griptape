# GalaxyBrain

[![PyPI Version](https://img.shields.io/pypi/v/galaxybrain.svg)](https://pypi.python.org/pypi/galaxybrain)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/gitbucket/gitbucket/blob/master/LICENSE)

_Turning LLMs into mighty shape rotators!_

GalaxyBrain is a workflow framework for large language models (LLMs). With GalaxyBrain, developers can define prompt completion steps, prompt rules, result validators, and more. Additionally, the framework adds memory capabilities to LLM workflows making it easy to handle state between steps.

## Goals

1. Reduce surprises when it comes to working with LLMs.
1. Focus on production use cases and CI/CD compatibility.
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
from galaxybrain.drivers import OpenAiDriver

load_dotenv()

api_key = os.environ.get('OPENAI_KEY')
driver = OpenAiDriver(api_key)
```


Here is an example of some of GalaxyBrain's functionality:

```python
from galaxybrain.rules import Rule, Validator
from galaxybrain.workflows import CompletionStep, Workflow
from galaxybrain.drivers import OpenAiDriver
from galaxybrain.prompts import Prompt
import galaxybrain.rules as rules


chat_rules = [
    rules.json.return_valid_json(),
    rules.json.put_answer_in_field("Names"),
    rules.conversation.be_truthful(),
    rules.conversation.your_name_is("GalaxyGPT"),
    Rule("only use information from fantasy novels")
]

driver = OpenAiDriver(temperature=0.5, user="demo")
workflow = Workflow(rules=chat_rules, driver=driver)

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

You can also validate results against your rules:

```python
validator = Validator(workflow.last_step().output, chat_rules)

if validator.validate():
    print("Rule validations passed")
else:
    print("Rule validations failed")
    print(validator.failed_rules())
```