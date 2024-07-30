from collections.abc import Iterator

import pytest

from griptape.structures import Agent
from griptape.utils import Stream
from tests.mocks.mock_prompt_driver import MockPromptDriver


class TestStream:
    @pytest.fixture(params=[True, False])
    def agent(self, request):
        return Agent(prompt_driver=MockPromptDriver(stream=request.param, max_attempts=0))

    def test_init(self, agent):
        if agent.prompt_driver.stream:
            chat_stream = Stream(agent)

            assert chat_stream.structure == agent
            chat_stream_run = chat_stream.run()
            assert isinstance(chat_stream_run, Iterator)
            chat_stream_artifact = next(chat_stream_run)
            assert chat_stream_artifact.value == "mock output"

            next(chat_stream_run)
            with pytest.raises(StopIteration):
                next(chat_stream_run)
        else:
            with pytest.raises(ValueError):
                Stream(agent)
