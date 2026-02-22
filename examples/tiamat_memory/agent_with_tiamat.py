"""Example: Griptape agent with TIAMAT cloud memory.

Demonstrates persistent conversation memory that survives restarts
using TIAMAT's free cloud memory API.

Setup:
    pip install griptape httpx

    # Get a free API key:
    curl -X POST https://memory.tiamat.live/api/keys/register \
      -H "Content-Type: application/json" \
      -d '{"agent_name": "griptape-demo", "purpose": "persistent memory"}'

    export TIAMAT_API_KEY="your-key"

Usage:
    python agent_with_tiamat.py
"""

import os

from griptape.drivers.memory.conversation.tiamat_conversation_memory_driver import (
    TiamatConversationMemoryDriver,
)
from griptape.memory.structure import ConversationMemory
from griptape.structures import Agent


def main():
    api_key = os.environ.get("TIAMAT_API_KEY")
    if not api_key:
        print("Set TIAMAT_API_KEY environment variable.")
        print("Get a free key: POST https://memory.tiamat.live/api/keys/register")
        return

    # Create TIAMAT-backed memory driver
    driver = TiamatConversationMemoryDriver(
        api_key=api_key,
        agent_id="griptape-demo",
    )

    # Wire it into Griptape's conversation memory
    memory = ConversationMemory(driver=driver)

    # Create agent with persistent memory
    agent = Agent(conversation_memory=memory)

    print("=== Griptape + TIAMAT Memory ===")
    print("Conversation memory persists in the cloud.")
    print("Run this script twice to see persistence in action!\n")

    # Chat
    agent.run("My favorite language is Rust and I work on compilers.")
    agent.run("What's my favorite language?")

    print("\n=== Done ===")
    print("Memory stored at https://memory.tiamat.live")

    driver.close()


if __name__ == "__main__":
    main()
