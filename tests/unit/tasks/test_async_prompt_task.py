import pytest

from griptape.tasks import PromptTask
from tests.mocks.mock_async_prompt_driver import MockAsyncPromptDriver


class TestAsyncPromptTask:
    @pytest.mark.asyncio
    async def test_async_run(self):
        """Test basic async_run functionality."""
        task = PromptTask("test", prompt_driver=MockAsyncPromptDriver())

        result = await task.async_run()

        assert result.to_text() == "mock output"

    @pytest.mark.asyncio
    async def test_async_try_run(self):
        """Test basic async_try_run functionality."""
        task = PromptTask("test", prompt_driver=MockAsyncPromptDriver())

        result = await task.async_try_run()

        assert result.to_text() == "mock output"

    @pytest.mark.asyncio
    async def test_async_with_sync_driver_raises_error(self):
        """Test that async_run raises an error when used with a sync driver."""
        from tests.mocks.mock_prompt_driver import MockPromptDriver

        task = PromptTask("test", prompt_driver=MockPromptDriver())

        with pytest.raises(ValueError, match="async_run\\(\\) requires an AsyncBasePromptDriver"):
            await task.async_run()

    @pytest.mark.asyncio
    async def test_async_default_run_actions_subtasks(self):
        """Test async actions subtask runner."""
        from griptape.artifacts import TextArtifact

        task = PromptTask("test", prompt_driver=MockAsyncPromptDriver())
        task.subtasks = []

        result = await task.async_default_run_actions_subtasks(TextArtifact("test input"))

        assert result.to_text() == "test input"

    @pytest.mark.asyncio
    async def test_async_default_run_output_schema_validation_subtasks(self):
        """Test async output schema validation subtask runner."""
        from griptape.artifacts import TextArtifact

        task = PromptTask("test", prompt_driver=MockAsyncPromptDriver(), output_schema=None)
        task.subtasks = []

        result = await task.async_default_run_output_schema_validation_subtasks(TextArtifact("test input"))

        assert result.to_text() == "test input"
