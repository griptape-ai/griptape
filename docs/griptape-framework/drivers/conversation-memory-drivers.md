---
search:
  boost: 2 
---

## Overview

You can persist and load memory by using Conversation Memory Drivers. You can build drivers for your own data stores by extending [BaseConversationMemoryDriver](../../reference/griptape/drivers/memory/conversation/base_conversation_memory_driver.md).

## Conversation Memory Drivers

### Local

The [LocalConversationMemoryDriver](../../reference/griptape/drivers/memory/conversation/local_conversation_memory_driver.md) allows you to persist Conversation Memory in a local JSON file.

```python
--8<-- "docs/griptape-framework/drivers/src/conversation_memory_drivers_1.py"
```

### Amazon DynamoDb

!!! info
    This driver requires the `drivers-memory-conversation-amazon-dynamodb` [extra](../index.md#extras).

The [AmazonDynamoDbConversationMemoryDriver](../../reference/griptape/drivers/memory/conversation/amazon_dynamodb_conversation_memory_driver.md) allows you to persist Conversation Memory in [Amazon DynamoDb](https://aws.amazon.com/dynamodb/).

```python
--8<-- "docs/griptape-framework/drivers/src/conversation_memory_drivers_2.py"
```
Optional parameters `sort_key` and `sort_key_value` can be supplied for tables with a composite primary key.


### Redis

!!! info
    This driver requires the `drivers-memory-conversation-redis` [extra](../index.md#extras).

The [RedisConversationMemoryDriver](../../reference/griptape/drivers/memory/conversation/redis_conversation_memory_driver.md) allows you to persist Conversation Memory in [Redis](https://redis.io/).

```python
--8<-- "docs/griptape-framework/drivers/src/conversation_memory_drivers_3.py"
```
