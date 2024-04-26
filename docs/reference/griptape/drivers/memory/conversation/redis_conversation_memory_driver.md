### Redis Conversation Memory Driver

!!! info
    This driver requires the `drivers-memory-conversation-redis` [extra](../../../../../griptape-framework/index.md#extras).

```python
import os
import uuid
from griptape.drivers import RedisConversationMemoryDriver
from griptape.memory.structure import ConversationMemory
from griptape.structures import Agent

conversation_id = uuid.uuid4().hex
redis_conversation_driver = RedisConversationMemoryDriver(
    host="127.0.0.1",
    port=6379,
    password='',
    index='griptape_converstaion',
    conversation_id = conversation_id
)

agent = Agent(conversation_memory=ConversationMemory(driver=redis_conversation_driver))

agent.run("My name is Jeff.")
agent.run("What is my name?")
```
