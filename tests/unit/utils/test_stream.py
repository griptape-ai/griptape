from collections.abc import Iterator
import pytest
from griptape.structures import Agent
from griptape.utils import Stream
from tests.mocks.mock_prompt_driver import MockPromptDriver
from tests.mocks.mock_tool.tool import MockTool


class TestStream:
    @pytest.fixture()
    def agent(self, request):
        return Agent(prompt_driver=MockPromptDriver(stream=True))

    @pytest.fixture()
    def agent_with_tools(self, request):
        return Agent(prompt_driver=MockPromptDriver(stream=True), tools=[MockTool(allowlist=["test"])])

    def test_stream_disabled(self, agent):
        agent = Agent(prompt_driver=MockPromptDriver(stream=False))

        with pytest.raises(ValueError):
            Stream(agent)

    def test_stream_run(self, agent):
        chat_stream = Stream(agent)

        assert chat_stream.structure == agent
        chat_stream_run = chat_stream.run()
        assert isinstance(chat_stream_run, Iterator)
        chat_stream_artifact = next(chat_stream_run)
        assert chat_stream_artifact.value == "mock output"

        with pytest.raises(StopIteration):
            next(chat_stream_run)
            next(chat_stream_run)

    def test_stream_run_with_tools(self, agent_with_tools):
        chat_stream = Stream(agent_with_tools)

        assert chat_stream.structure == agent_with_tools
        chat_stream_run = chat_stream.run()
        assert isinstance(chat_stream_run, Iterator)
        chat_stream_artifact = next(chat_stream_run)
        assert chat_stream_artifact.value == "\nMockTool.test (test-id)"
        chat_stream_artifact = next(chat_stream_run)
        assert chat_stream_artifact.value == "mock input"

        with pytest.raises(StopIteration):
            next(chat_stream_run)
            next(chat_stream_run)
