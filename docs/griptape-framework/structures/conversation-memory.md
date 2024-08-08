---
search:
  boost: 2 
---

## Overview

You can use Conversation Memory to give Griptape Structures the ability to keep track of the conversation across runs. All structures are created with [ConversationMemory](../../reference/griptape/memory/structure/conversation_memory.md) by default.

### Example

```python
--8<-- "docs/griptape-framework/structures/src/conversation_memory_1.py"
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
--8<-- "docs/griptape-framework/structures/src/conversation_memory_2.py"
```

## Types of Memory

Griptape provides several types of Conversation Memory to fit various use-cases.

### Conversation Memory

[ConversationMemory](../../reference/griptape/memory/structure/conversation_memory.md) will keep track of the full task input and output for all runs.

```python
--8<-- "docs/griptape-framework/structures/src/conversation_memory_3.py"
```

You can set the [max_runs](../../reference/griptape/memory/structure/base_conversation_memory.md#griptape.memory.structure.base_conversation_memory.BaseConversationMemory.max_runs) parameter to limit how many runs are kept in memory.

```python
--8<-- "docs/griptape-framework/structures/src/conversation_memory_4.py"
```

### Summary Conversation Memory

[SummaryConversationMemory](../../reference/griptape/memory/structure/summary_conversation_memory.md) will progressively summarize task input and output of runs.

You can choose to offset which runs are summarized with the
[offset](../../reference/griptape/memory/structure/summary_conversation_memory.md#griptape.memory.structure.summary_conversation_memory.SummaryConversationMemory.offset) parameter.

```python
--8<-- "docs/griptape-framework/structures/src/conversation_memory_5.py"
```

