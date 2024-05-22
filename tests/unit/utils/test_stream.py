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
        return Agent(
            prompt_driver=MockPromptDriver(stream=True, emulate_cot=True, use_native_tools=True),
            tools=[MockTool(allowlist=["test"], off_prompt=False)],
        )

    def test_stream_disabled(self, agent):
        agent = Agent(prompt_driver=MockPromptDriver(stream=False))

        with pytest.raises(ValueError):
            Stream(agent)

    def test_stream_run(self, agent):
        chat_stream = Stream(agent)

        assert chat_stream.structure == agent
        chat_stream_run = chat_stream.run()
        assert isinstance(chat_stream_run, Iterator)
        assert next(chat_stream_run).value == "mock output"
        assert next(chat_stream_run).value == "\n"

        with pytest.raises(StopIteration):
            next(chat_stream_run)

    def test_stream_run_with_tools(self, agent_with_tools):
        chat_stream = Stream(agent_with_tools)

        assert chat_stream.structure == agent_with_tools
        chat_stream_run = chat_stream.run()
        assert isinstance(chat_stream_run, Iterator)

        assert next(chat_stream_run).value == "mock thought"
        assert next(chat_stream_run).value == "\nMockTool.test (test-id)"
        assert next(chat_stream_run).value == '{"values": {"test": "mock tool input"}}'
        assert next(chat_stream_run).value == "\n"
        assert next(chat_stream_run).value == "Answer: mock output"
        assert next(chat_stream_run).value == "\n"

        with pytest.raises(StopIteration):
            next(chat_stream_run)
