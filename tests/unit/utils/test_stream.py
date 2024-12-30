import json
from collections.abc import Iterator

import pytest

from griptape.structures import Agent
from griptape.utils import Stream
from tests.mocks.mock_prompt_driver import MockPromptDriver
from tests.mocks.mock_tool.tool import MockTool


class TestStream:
    @pytest.mark.parametrize("stream", [True, False])
    @pytest.mark.parametrize("use_native_tools", [True, False])
    def test_init(self, stream, use_native_tools):
        prompt_driver = MockPromptDriver(use_native_tools=use_native_tools, stream=stream)
        agent = Agent(tools=[MockTool()], prompt_driver=prompt_driver)
        chat_stream = Stream(agent)

        chat_stream_run = chat_stream.run()
        assert chat_stream.structure == agent
        assert isinstance(chat_stream_run, Iterator)
        if prompt_driver.stream:
            if use_native_tools:
                assert next(chat_stream_run).value == "MockTool.mock-tag (test)"
                assert next(chat_stream_run).value == json.dumps({"values": {"test": "test-value"}}, indent=2)
                next(chat_stream_run)
                assert next(chat_stream_run).value == "Answer: mock output"
                next(chat_stream_run)
                with pytest.raises(StopIteration):
                    next(chat_stream_run)
            else:
                assert next(chat_stream_run).value == "mock output"
        else:
            # MockPromptDriver produces some extra events because it simulates CoT when using native tools.
            if use_native_tools:
                assert next(chat_stream_run).value == "\n"
                assert next(chat_stream_run).value == "\n"
                with pytest.raises(StopIteration):
                    next(chat_stream_run)
            else:
                assert next(chat_stream_run).value == "\n"
                with pytest.raises(StopIteration):
                    next(chat_stream_run)
