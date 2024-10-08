# Threads

A [Thread can be created](https://cloud.griptape.ai/threads/create) to store conversation history across any LLM invocation. A Thread contains a list of [Messages](https://cloud.griptape.ai/messages/create). Messages can be updated and deleted, in order to control how the LLM recalls past conversations.

A Thread can be given an `alias` so it can be referenced by a user-provided unique identifier:

```bash
export GT_CLOUD_API_KEY=<your API key here>
export ALIAS=<your thread alias>
curl -H "Authorization: Bearer ${GT_CLOUD_API_KEY}" https://cloud.griptape.ai/api/threads?alias=${ALIAS}
```
