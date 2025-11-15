"""Example demonstrating async Agent usage.

This example shows:
1. Basic async Agent.async_run() usage
2. Using async Agent with tools
3. Using async event listeners with Agent
"""

import asyncio
import os

from griptape.drivers.prompt import AsyncOpenAiChatPromptDriver
from griptape.events import EventListener, FinishPromptEvent, StartPromptEvent
from griptape.structures import Agent
from griptape.tools import Calculator, WebScraper


async def async_event_handler(event):
    """Async event handler for monitoring Agent execution."""
    if isinstance(event, StartPromptEvent):
        print(f"[EVENT] Starting prompt with model: {event.model}")
    elif isinstance(event, FinishPromptEvent):
        print(f"[EVENT] Finished prompt. Tokens used: {event.input_token_count + event.output_token_count}")
    return event


async def basic_example():
    """Basic async Agent example."""
    print("=== Basic Async Agent Example ===")

    driver = AsyncOpenAiChatPromptDriver(model="gpt-4o-mini", api_key=os.environ.get("OPENAI_API_KEY"))

    agent = Agent(prompt_driver=driver)

    result = await agent.async_run("What is the capital of France?")
    print(f"Result: {result.output.to_text()}\n")


async def tools_example():
    """Async Agent with tools example."""
    print("=== Async Agent with Tools Example ===")

    driver = AsyncOpenAiChatPromptDriver(model="gpt-4o-mini", api_key=os.environ.get("OPENAI_API_KEY"))

    agent = Agent(prompt_driver=driver, tools=[Calculator()])

    result = await agent.async_run("What is 1337 * 42?")
    print(f"Result: {result.output.to_text()}\n")


async def event_listener_example():
    """Async Agent with event listener example."""
    print("=== Async Agent with Event Listener Example ===")

    driver = AsyncOpenAiChatPromptDriver(model="gpt-4o-mini", api_key=os.environ.get("OPENAI_API_KEY"))

    agent = Agent(prompt_driver=driver)

    async with EventListener(on_event=async_event_handler):
        result = await agent.async_run("Write a haiku about async programming")
        print(f"Result: {result.output.to_text()}\n")


async def streaming_example():
    """Async Agent with streaming example."""
    print("=== Async Agent with Streaming Example ===")

    from griptape.events import TextChunkEvent

    driver = AsyncOpenAiChatPromptDriver(model="gpt-4o-mini", api_key=os.environ.get("OPENAI_API_KEY"), stream=True)

    agent = Agent(prompt_driver=driver)

    async def on_chunk(event):
        if isinstance(event, TextChunkEvent):
            print(event.token, end="", flush=True)
        return event

    async with EventListener(on_event=on_chunk):
        result = await agent.async_run("Count from 1 to 5")
        print(f"\n\nFinal result: {result.output.to_text()}\n")


async def main():
    """Run all async Agent examples."""
    await basic_example()
    await tools_example()
    await event_listener_example()
    await streaming_example()


if __name__ == "__main__":
    asyncio.run(main())
