# GalaxyBrain

[![PyPI Version](https://img.shields.io/pypi/v/galaxybrain.svg)](https://pypi.python.org/pypi/galaxybrain)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/gitbucket/gitbucket/blob/master/LICENSE)

_Turning LLMs into mighty shape rotators!_

## Goals

1. Reduce surprises when it comes to working with LLMs.
1. Focus on production use cases and CI/CD compatibility.
1. Avoid bloat and keep base primitives simple.

## Getting Started
First, install the library:

```
pip install galaxybrain
```

Currently, GalaxyBrain only supports OpenAI APIs, so you'll need to [get an API key](https://beta.openai.com/account/api-keys). You can then either keep it on your path as `OPENAI_API_KEY` or pass it to the completion object manually:

```python
api_key = ...
OpenAiCompletion(api_key)
```

Here is an example of some of GalaxyBrain's functionality:

```python
from galaxybrain.completions import OpenAiCompletion
from galaxybrain.memory import Memory
from galaxybrain.prompts import Prompt
import galaxybrain.rules.json as json_rules
from galaxybrain.completions import Validator


completion = OpenAiCompletion(api_key, temperature=0.9, user="demo")
memory = Memory()
rules = [
    json_rules.return_valid_json(),
    json_rules.put_answer_in_field("Names"),
    Rule("only use information from fantasy novels")
]

completion.complete(
    Prompt("Give me ideas for two names from the same universe", memory=memory, rules=rules)
)

# Output:
# {
#     "Names": ["Frodo Baggins", "Gandalf the Grey"]
# }

result = completion.complete(
    Prompt("Give me 3 more from another universe", memory=memory)
)

# Output:
# {
#     "Names": ["Dumbledore", "Luna Lovegood", "Harry Potter"]
# }
```

You can also validate results against your rules:

```python
validator = Validator(result, rules)

if validator.validate():
    print("Rule validations passed")
else:
    print("Rule validations failed")
    print(validator.failed_rules())
```