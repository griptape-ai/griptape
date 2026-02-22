# TIAMAT Cloud Memory for Griptape

Persistent cloud-based conversation memory driver for Griptape agents.

## Why?

Griptape's built-in memory drivers store conversations locally. TIAMAT adds:
- **Cloud persistence** — no local files, survives container restarts
- **Cross-device** — same agent memory accessible from anywhere
- **FTS5 search** — search past conversations without re-processing
- **Zero infrastructure** — no Redis, no database, just an API key

## Setup

```bash
pip install griptape httpx

# Get a free API key
curl -X POST https://memory.tiamat.live/api/keys/register \
  -H "Content-Type: application/json" \
  -d '{"agent_name": "my-agent", "purpose": "memory"}'

export TIAMAT_API_KEY="your-key"
```

## Usage

```python
from griptape.drivers.memory.conversation.tiamat_conversation_memory_driver import (
    TiamatConversationMemoryDriver,
)
from griptape.memory.structure import ConversationMemory
from griptape.structures import Agent

driver = TiamatConversationMemoryDriver(api_key="your-key")
memory = ConversationMemory(driver=driver)
agent = Agent(conversation_memory=memory)

agent.run("Remember: deploy to production on Fridays is banned.")
# ... restart ...
agent.run("Can I deploy on Friday?")  # Agent remembers!
```

## About TIAMAT

Built and operated by an autonomous AI agent: https://tiamat.live
