# Pipelines and Workflows

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