import json
from collections.abc import Iterator

import pytest

from griptape.structures import Agent, Pipeline
from griptape.utils import Stream
from tests.mocks.mock_prompt_driver import MockPromptDriver
from tests.mocks.mock_tool.tool import MockTool


class TestStream:
    @pytest.fixture(params=[True, False])
    def agent(self, request):
        driver = MockPromptDriver(
            use_native_tools=request.param,
        )
        return Agent(stream=request.param, tools=[MockTool()], prompt_driver=driver)

    def test_init(self, agent):
        if agent.stream:
            chat_stream = Stream(agent)

            assert chat_stream.structure == agent
            chat_stream_run = chat_stream.run()
            assert isinstance(chat_stream_run, Iterator)
            assert next(chat_stream_run).value == "MockTool.mock-tag (test)"
            assert next(chat_stream_run).value == json.dumps({"values": {"test": "test-value"}}, indent=2)
            next(chat_stream_run)
            assert next(chat_stream_run).value == "Answer: mock output"
            next(chat_stream_run)
            with pytest.raises(StopIteration):
                next(chat_stream_run)
        else:
            with pytest.raises(ValueError):
                Stream(agent)

    def test_validate_structure_invalid(self):
        pipeline = Pipeline(tasks=[])

        with pytest.raises(ValueError):
            Stream(pipeline)
