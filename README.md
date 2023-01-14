# GalaxyBrain

_Turning wordcel LLMs into mighty shape rotators!_

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
completion = OpenAiCompletion(api_key, temperature=0.9, user="demo")
memory = Memory()
rules = [
    PromptRule(
        "act as a web API and only output valid JSON",
        validator=lambda v : is_valid_json(v)
    ),
    PromptRule(
        "output JSON field name is 'Output'",
        validator=lambda v : has_key_in_json_object(v, "Output")
    )
]

completion.complete(
    Prompt("Give me 2 fantasy character name ideas in an array", memory=memory, rules=rules)
)

# Output:
# {
#     "Output": ["Gwendoline the Wizard", "Krastov the Barbarian"]
# }

completion.complete(
    Prompt("Give me 2 more", memory=memory)
)

# Output
# {
#     "Output": ["Lysander the Warlock", "Ltamos the Elf"]
# }
```