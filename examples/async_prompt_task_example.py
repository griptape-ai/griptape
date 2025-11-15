"""Example of using PromptTask with AsyncOpenAiChatPromptDriver.

This example demonstrates how to use the async API with PromptTask.
The subtask_runners are automatically converted from sync to async.
"""

import asyncio
import os

from griptape.drivers.prompt import AsyncOpenAiChatPromptDriver
from griptape.tasks import PromptTask


async def main():
    """Run a simple async prompt task."""
    # Create an async driver
    driver = AsyncOpenAiChatPromptDriver(
        model="gpt-4o-mini",
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    # Create a PromptTask with the async driver
    # The default subtask_runners will be automatically converted to async
    task = PromptTask(
        prompt_driver=driver,
        input="What is the capital of France? Answer in one sentence.",
    )

    # Run the task asynchronously
    print("Running async PromptTask...")
    result = await task.async_run()

    print(f"Result: {result.to_text()}")


if __name__ == "__main__":
    asyncio.run(main())
