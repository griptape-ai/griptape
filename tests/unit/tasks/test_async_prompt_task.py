import asyncio

import pytest

from griptape.tasks import PromptTask
from tests.mocks.mock_async_prompt_driver import MockAsyncPromptDriver


class TestAsyncPromptTask:
    def test_async_run(self):
        """Test basic async_run functionality."""

        async def _test():
            task = PromptTask("test", prompt_driver=MockAsyncPromptDriver())
            result = await task.async_run()
            assert result.to_text() == "mock output"

        asyncio.run(_test())

    def test_async_try_run(self):
        """Test basic async_try_run functionality."""

        async def _test():
            task = PromptTask("test", prompt_driver=MockAsyncPromptDriver())
            result = await task.async_try_run()
            assert result.to_text() == "mock output"

        asyncio.run(_test())

    def test_async_default_run_actions_subtasks(self):
        """Test async actions subtask runner."""

        async def _test():
            from griptape.artifacts import TextArtifact

            task = PromptTask("test", prompt_driver=MockAsyncPromptDriver())
            task.subtasks = []

            result = await task.async_default_run_actions_subtasks(TextArtifact("test input"))

            assert result.to_text() == "test input"

        asyncio.run(_test())

    def test_async_default_run_output_schema_validation_subtasks(self):
        """Test async output schema validation subtask runner."""

        async def _test():
            from griptape.artifacts import TextArtifact

            task = PromptTask("test", prompt_driver=MockAsyncPromptDriver(), output_schema=None)
            task.subtasks = []

            result = await task.async_default_run_output_schema_validation_subtasks(TextArtifact("test input"))

            assert result.to_text() == "test input"

        asyncio.run(_test())
