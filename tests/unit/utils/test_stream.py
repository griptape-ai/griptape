from collections.abc import Iterator

import pytest

from griptape.structures import Agent, Pipeline
from griptape.utils import Stream


class TestStream:
    @pytest.fixture(params=[True, False])
    def agent(self, request):
        return Agent(stream=request.param)

    def test_init(self, agent):
        if agent.stream:
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

    def test_validate_structure_invalid(self):
        pipeline = Pipeline(tasks=[])

        with pytest.raises(ValueError):
            Stream(pipeline)
