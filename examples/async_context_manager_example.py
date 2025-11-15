"""Example demonstrating EventListener as both sync and async context manager.

This example shows:
1. Using EventListener with sync context manager (with statement)
2. Using EventListener with async context manager (async with statement)
3. Async event handlers with async context manager
"""

import asyncio
import os

from griptape.drivers.prompt import AsyncOpenAiChatPromptDriver, OpenAiChatPromptDriver
from griptape.events import EventListener, FinishPromptEvent, StartPromptEvent
from griptape.tasks import PromptTask


def sync_event_handler(event):
    """Sync event handler for demonstration."""
    if isinstance(event, StartPromptEvent):
        print(f"[SYNC] Starting prompt with model: {event.model}")
    elif isinstance(event, FinishPromptEvent):
        print(f"[SYNC] Finished prompt")
    return event


async def async_event_handler(event):
    """Async event handler that can perform async operations."""
    if isinstance(event, StartPromptEvent):
        print(f"[ASYNC] Starting prompt with model: {event.model}")
        # Could perform async operations here like logging to a database
        await asyncio.sleep(0.01)
    elif isinstance(event, FinishPromptEvent):
        print(f"[ASYNC] Finished prompt")
        await asyncio.sleep(0.01)
    return event


def sync_example():
    """Example using sync context manager with sync event handler."""
    print("=== Sync Example ===")
    driver = OpenAiChatPromptDriver(model="gpt-4o-mini", api_key=os.environ.get("OPENAI_API_KEY"))

    task = PromptTask(prompt_driver=driver, input="Say hello in one word.")

    # Use sync context manager with sync handler
    with EventListener(on_event=sync_event_handler):
        result = task.run()
        print(f"Result: {result.to_text()}\n")


async def async_example():
    """Example using async context manager with async event handler."""
    print("=== Async Example ===")
    driver = AsyncOpenAiChatPromptDriver(model="gpt-4o-mini", api_key=os.environ.get("OPENAI_API_KEY"))

    task = PromptTask(prompt_driver=driver, input="Say hello in one word.")

    # Use async context manager with async handler
    async with EventListener(on_event=async_event_handler):
        result = await task.async_run()
        print(f"Result: {result.to_text()}\n")


async def main():
    """Run both sync and async examples."""
    # Sync example with sync context manager
    sync_example()

    # Async example with async context manager
    await async_example()


if __name__ == "__main__":
    asyncio.run(main())
