"""Example of using async event listeners with AsyncOpenAiChatPromptDriver.

This example demonstrates how to use async event handlers with the event system.
"""

import asyncio
import os

from griptape.drivers.prompt import AsyncOpenAiChatPromptDriver
from griptape.events import EventListener, FinishPromptEvent, StartPromptEvent, TextChunkEvent
from griptape.tasks import PromptTask


async def async_event_handler(event):
    """Async event handler that can perform async operations."""
    if isinstance(event, StartPromptEvent):
        print(f"[ASYNC] Starting prompt with model: {event.model}")
    elif isinstance(event, FinishPromptEvent):
        print(
            f"[ASYNC] Finished prompt. Input tokens: {event.input_token_count}, Output tokens: {event.output_token_count}"
        )
    elif isinstance(event, TextChunkEvent):
        print(f"[ASYNC] Received text chunk: {event.token}")
    return event


async def main():
    """Run async prompt task with async event listener."""
    # Create an async driver with streaming enabled
    driver = AsyncOpenAiChatPromptDriver(
        model="gpt-4o-mini",
        api_key=os.environ.get("OPENAI_API_KEY"),
        stream=True,
    )

    # Create a PromptTask with the async driver
    task = PromptTask(
        prompt_driver=driver,
        input="Write a haiku about async programming.",
    )

    # Register an async event listener using async context manager
    async with EventListener(on_event=async_event_handler):
        print("Running async PromptTask with async event listener...")
        result = await task.async_run()

        print(f"\nFinal Result: {result.to_text()}")


if __name__ == "__main__":
    asyncio.run(main())
