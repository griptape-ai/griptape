import asyncio

import pytest

from griptape.structures import Agent
from tests.mocks.mock_async_prompt_driver import MockAsyncPromptDriver


class TestAsyncAgent:
    def test_async_run(self):
        """Test basic async_run functionality."""

        async def _test():
            agent = Agent(prompt_driver=MockAsyncPromptDriver())
            result = await agent.async_run("test input")
            assert result.output.to_text() == "mock output"

        asyncio.run(_test())

    def test_async_run_multiple_times(self):
        """Test async_run can be called multiple times."""

        async def _test():
            agent = Agent(prompt_driver=MockAsyncPromptDriver())

            # First run
            result1 = await agent.async_run("first input")
            assert result1.output.to_text() == "mock output"

            # Second run
            result2 = await agent.async_run("second input")
            assert result2.output.to_text() == "mock output"

        asyncio.run(_test())

    def test_async_try_run(self):
        """Test basic async_try_run functionality."""

        async def _test():
            agent = Agent(prompt_driver=MockAsyncPromptDriver())
            result = await agent.async_try_run("test input")
            assert result.output.to_text() == "mock output"

        asyncio.run(_test())

    def test_async_run_with_sync_driver_raises_error(self):
        """Test that async_run raises an error when used with a sync driver."""

        async def _test():
            from tests.mocks.mock_prompt_driver import MockPromptDriver

            agent = Agent(prompt_driver=MockPromptDriver())

            with pytest.raises(ValueError, match="async_run\\(\\) requires an AsyncBasePromptDriver"):
                await agent.async_run("test input")

        asyncio.run(_test())

    def test_async_run_preserves_conversation_memory(self):
        """Test that async_run preserves conversation memory."""

        async def _test():
            agent = Agent(prompt_driver=MockAsyncPromptDriver())

            # First run
            await agent.async_run("first input")
            assert len(agent.conversation_memory.runs) == 1

            # Second run
            await agent.async_run("second input")
            assert len(agent.conversation_memory.runs) == 2

        asyncio.run(_test())
