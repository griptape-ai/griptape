import pytest

from tests.mocks.mock_chunk_event import MockChunkEvent


class TestBaseChunkEvent:
    @pytest.fixture()
    def base_chunk_event(self):
        return MockChunkEvent(token="foo", index=1)

    def test_token(self, base_chunk_event):
        assert base_chunk_event.index == 1
        assert base_chunk_event.token == "foo"
        assert str(base_chunk_event) == "mock foo"

    def test_to_dict(self, base_chunk_event):
        assert base_chunk_event.to_dict()["index"] == 1
        assert base_chunk_event.to_dict()["token"] == "foo"
