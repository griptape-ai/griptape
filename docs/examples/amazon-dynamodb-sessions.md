Griptape provides [Conversation Memory](../griptape-framework/structures/conversation-memory.md) as a means of persisting conversation context across multiple Structure runs.
If you provide it with a suitable Driver, the memory of the previous conversation can be preserved between run of a Structure, giving it additional context for how to respond.
While we can use the [LocalConversationMemoryDriver](../griptape-framework/drivers/conversation-memory-drivers.md#local) to store the conversation history in a local file, in production use-cases we may want to store in a proper database.

In this example, we will show you how to use the [AmazonDynamoDbConversationMemoryDriver](../griptape-framework/drivers/conversation-memory-drivers.md#amazon-dynamodb) to persist the memory in an [Amazon DynamoDB](https://aws.amazon.com/dynamodb/) table. Please refer to the [Amazon DynamoDB documentation](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/getting-started-step-1.html) for information on setting up DynamoDB. 

This code implements the idea of a generic "Session" that represents a Conversation Memory entry. For example, a "Session" could be used to represent an individual user's conversation, or a group conversation thread.

```python
--8<-- "docs/examples/src/amazon_dynamodb_sessions_1.py"
```

Conversation Memory for an individual user:

```bash
python session.py "Hello my name is Collin." "user-id-123"
python session.py "What is my name?" "user-id-123"
```

```
> Hello Collin! How can I assist you today?
> Your name is Collin.
```

```json
{
  "id": {
    "S": "user-id-123"
  },
  "value": {
    "S": "{\"type\": \"ConversationMemory\", \"runs\": [{\"type\": \"Run\", \"id\": \"8c403fb92b134b14a0af8847e52e6212\", \"input\": \"Hello my name is Collin.\", \"output\": \"Hello Collin! How can I assist you today?\"}, {\"type\": \"Run\", \"id\": \"706d9fb072ca49e192bfed7fc1964925\", \"input\": \"What is my name?\", \"output\": \"Your name is Collin.\"}], \"max_runs\": null}"
  }
}
```

Conversation Memory for a group of users:

```bash
python session.py "Hello my name is Zach." "group-id-122"
python session.py "And I'm Matt" "group-id-123"
python session.py "And I'm Collin, who all is here?" "group-id-123"
```

```
> Hello Zach! How can I assist you today?
> Hello Matt! Nice to meet you too. How can I help you today?
> Hello Collin! So far, we have Zach, Matt, and now you. How can I assist you all today?
```

```json
{
  "id": {
    "S": "group-id-123"
  },
  "value": {
    "S": "{\"type\": \"ConversationMemory\", \"runs\": [{\"type\": \"Run\", \"id\": \"b612cdf5908845e392c026e1cf00460b\", \"input\": \"Hello my name is Zach.\", \"output\": \"Hello Zach! How can I assist you today?\"}, {\"type\": \"Run\", \"id\": \"4507988d82164cad8a288da8c984817c\", \"input\": \"And I'm Matt\", \"output\": \"Hello Matt! Nice to meet you too. How can I help you today?\"}, {\"type\": \"Run\", \"id\": \"65a70c22dae24655b312cf8eaa649bfd\", \"input\": \"And I'm Collin, who all is here?\", \"output\": \"Hello Collin! So far, we have Zach, Matt, and now you. How can I assist you all today?\"}], \"max_runs\": null}"
  }
}
```
