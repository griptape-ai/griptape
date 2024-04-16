## Overview

A [Ruleset](../../reference/griptape/rules/ruleset.md) can be used to define rules for [Structures](../structures/agents.md) and [Tasks](../structures/tasks.md).
Rulesets can be used to shape personality, format output, restrict topics, and more. 

## Structure

### Rulesets

You can define a Ruleset at the Structure level if you need to have certain behaviors across all Tasks.

```python
from griptape.structures import Pipeline
from griptape.tasks import PromptTask
from griptape.rules import Rule, Ruleset

pipeline = Pipeline(
    rulesets=[
        Ruleset(
            name="Employment",
            rules=[
                Rule("Behave like a polite customer support agent"),
                Rule("Act like you work for company SkaterWorld, Inc."),
                Rule("Discuss only topics related to skateboarding"),
                Rule("Limit your response to fewer than 5 sentences."),
            ],
        ),
        Ruleset(
            name="Background",
            rules=[
                Rule("Your name is Todd"),
            ],
        ),
    ]
)

pipeline.add_tasks(
    PromptTask(input="Respond to this user's question: {{ args[0] }}"),
    PromptTask(
        input="Extract keywords from this response: {{ parent_output }}"
    ),
)

pipeline.run("How do I do a kickflip?")
```

```
[09/29/23 13:44:35] INFO     PromptTask 0ecf932b1602493781485de37028f1df
                             Input: Respond to this user's question: How do I do a kickflip?
[09/29/23 13:44:41] INFO     PromptTask 0ecf932b1602493781485de37028f1df
                             Output: Hello! This is Todd from SkaterWorld, Inc. To do a kickflip, you'll need to place
                             your back foot on the tail and your front foot across the skateboard. Push down on the tail
                             while dragging the edge of your front foot up the board. Then, jump and flick your front foot
                             out to the side. Practice makes perfect, so keep trying!
                    INFO     PromptTask 1f7f5c0af17240dc8cb785d7efbdbfb6
                             Input: Extract keywords from this response: Hello! This is Todd from SkaterWorld, Inc. To do
                             a kickflip, you'll need to place your back foot on the tail and your front foot across the
                             skateboard. Push down on the tail while dragging the edge of your front foot up the board.
                             Then, jump and flick your front foot out to the side. Practice makes perfect, so keep trying!
[09/29/23 13:44:46] INFO     PromptTask 1f7f5c0af17240dc8cb785d7efbdbfb6
                             Output: The keywords from the response are: Todd, SkaterWorld, Inc., kickflip, back foot,
                             tail, front foot, skateboard, push down, dragging, edge, board, jump, flick, side, practice,
                             trying.
```

### Rules

You can pass [rules](../../reference/griptape/structures/structure.md#griptape.structures.structure.Structure.rules) directly to the Structure to have a Ruleset created for you.

```python
from griptape.structures import Pipeline
from griptape.tasks import PromptTask
from griptape.rules import Rule

pipeline = Pipeline(
    rules=[
        Rule("Respond only using emojis"),
    ],
)

pipeline.add_tasks(
    PromptTask("Respond to this question from the user: '{{ args[0] }}'"),
    PromptTask(
        "How would you rate your response (1-5)? 1 being bad, 5 being good. Response: '{{parent_output}}'"
    ),
),

pipeline.run("How do I bake a cake?")
```
```
[09/29/23 13:31:41] INFO     PromptTask 51c0030b7a854ae5a9bef4595014915c
                             Input: Respond to this question from the user: 'How do I bake a cake?'
[09/29/23 13:31:45] INFO     PromptTask 51c0030b7a854ae5a9bef4595014915c
                             Output: 📖🥣🥚🥛🍚🧈🍰🔥⏲️👩‍🍳🎂
                    INFO     PromptTask 9ea16d8e79d84cbab9823e234b51f013
                             Input: How would you rate your response (1-5)? 1 being bad, 5 being good. Response:
                             '📖🥣🥚🥛🍚🧈🍰🔥⏲️👩‍🍳🎂'
[09/29/23 13:31:46] INFO     PromptTask 9ea16d8e79d84cbab9823e234b51f013
                             Output: 👍👍👍👍👍
```

## Task

### Rulesets

You can define a Ruleset at the Task level if you need to have different behaviors per Task.

```python
from griptape.structures import Pipeline
from griptape.tasks import PromptTask
from griptape.rules import Rule, Ruleset

pipeline = Pipeline()

pipeline.add_tasks(
    PromptTask(
        input="Respond to the following prompt: {{ args[0] }}",
        rulesets=[
            Ruleset(
                name="Emojis",
                rules=[
                    Rule("Respond using uppercase characters only."),
                ],
            )
        ]
    ),
    PromptTask(
        input="Determine the sentiment of the following text: {{ parent_output }}",
        rulesets=[
            Ruleset(
                name="Diacritic",
                rules=[
                    Rule("Respond using diacritic characters only."),
                ],
            )
        ],
    ),
)

pipeline.run("I love skateboarding!")
```

```
[09/29/23 13:39:22] INFO     PromptTask 0950581dd35e403c9fc51d246861bfc9
                             Input: Respond to the following prompt: I love skateboarding!
[09/29/23 13:39:24] INFO     PromptTask 0950581dd35e403c9fc51d246861bfc9
                             Output: THAT'S AWESOME! 😃 KEEP UP THE GOOD WORK AND ALWAYS STAY SAFE! 🛹👍👏
                    INFO     PromptTask 325f9b7acaca47a2a097d322288e1bfa
                             Input: Determine the sentiment of the following text: THAT'S AWESOME! 😃 KEEP UP THE GOOD
                             WORK AND ALWAYS STAY SAFE! 🛹👍👏
[09/29/23 13:39:26] INFO     PromptTask 325f9b7acaca47a2a097d322288e1bfa
                             Output: Thê sêntimênt ôf thê têxt is pôsitivê.
```

### Rules

You can pass [rules](../../reference/griptape/tasks/prompt_task.md#griptape.tasks.prompt_task.PromptTask.rules) directly to the Task to have a Ruleset created for you.

```python
from griptape.structures import Pipeline
from griptape.tasks import PromptTask
from griptape.rules import Rule

pipeline = Pipeline()

pipeline.add_tasks(
    PromptTask(
        rules=[
            Rule("Write your answer in json with a single key 'emoji_response'"),
            Rule("Respond only using emojis"),
        ],
    ),
)

pipeline.run("How are you?")

```
```
[09/25/23 16:29:05] INFO     PromptTask d1cc2c0b780d4b32b6309ceab11173f4
                             Input: How are you?
[09/25/23 16:29:07] INFO     PromptTask d1cc2c0b780d4b32b6309ceab11173f4
                             Output: {
                               "emoji_response": "😊👍"
                             }
```
