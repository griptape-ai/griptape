## Overview

You can use Conversation Memory to give Griptape Structures the ability to keep track of the conversation across runs. All structures are created with [ConversationMemory](../../reference/griptape/memory/structure/conversation_memory.md) by default.

### Example

```python
from griptape.structures import Agent
from griptape.memory.structure import ConversationMemory

agent = Agent()

agent.run("My favorite animal is a Liger.")
agent.run("What is my favorite animal?")
```

```
[09/19/23 14:21:07] INFO     PromptTask 3e64ca5d5f634a11957cbf46adce251a
                             Input: My favorite animal is a Liger.
[09/19/23 14:21:13] INFO     PromptTask 3e64ca5d5f634a11957cbf46adce251a
                             Output: That's fascinating! Ligers, a hybrid offspring of a male lion and a female tiger, are indeed unique and
                             interesting animals. They are known to be the largest of all big cats. Do you have a particular reason why you
                             like them so much?
                    INFO     PromptTask 3e64ca5d5f634a11957cbf46adce251a
                             Input: What is my favorite animal?
[09/19/23 14:21:15] INFO     PromptTask 3e64ca5d5f634a11957cbf46adce251a
                             Output: Your favorite animal is a Liger, as you previously mentioned.
```

You can disable conversation memory in any structure by setting it to `None`:

```python
from griptape.structures import Agent
from griptape.memory.structure import ConversationMemory

Agent(conversation_memory=None)
```

## Types of Memory

Griptape provides several types of Conversation Memory to fit various use-cases.

### Conversation Memory

[ConversationMemory](../../reference/griptape/memory/structure/conversation_memory.md) will keep track of the full task input and output for all runs.

```python
from griptape.structures import Agent
from griptape.memory.structure import ConversationMemory

agent = Agent(
    conversation_memory=ConversationMemory()
)

agent.run("Hello!")

print(agent.conversation_memory)
```

You can set the [max_runs](../../reference/griptape/memory/structure/conversation_memory.md#griptape.memory.structure.conversation_memory.ConversationMemory.max_runs) parameter to limit how many runs are kept in memory.

```python
from griptape.structures import Agent
from griptape.memory.structure import ConversationMemory

agent = Agent(
    conversation_memory=ConversationMemory(max_runs=2)
)

agent.run("Run 1")
agent.run("Run 2")
agent.run("Run 3")
agent.run("Run 4")
agent.run("Run 5")

print(agent.conversation_memory.runs[0].input == 'run4')
print(agent.conversation_memory.runs[1].input == 'run5')
```

### Summary Conversation Memory

[SummaryConversationMemory](../../reference/griptape/memory/structure/summary_conversation_memory.md) will progressively summarize task input and output of runs.

You can choose to offset which runs are summarized with the
[offset](../../reference/griptape/memory/structure/summary_conversation_memory.md#griptape.memory.structure.summary_conversation_memory.SummaryConversationMemory.offset) parameter.

```python
from griptape.structures import Agent
from griptape.memory.structure import SummaryConversationMemory

agent = Agent(
    conversation_memory=SummaryConversationMemory(offset=2)
)

agent.run("Hello!")

print(agent.conversation_memory.summary)
```

