import pytest

from griptape.events import BaseChunkEvent


class TestBaseChunkEvent:
    @pytest.fixture()
    def base_chunk_event(self):
        return BaseChunkEvent(index=1)

    def test_token(self, base_chunk_event):
        assert base_chunk_event.index == 1

    def test_to_dict(self, base_chunk_event):
        assert base_chunk_event.to_dict()["index"] == 1
