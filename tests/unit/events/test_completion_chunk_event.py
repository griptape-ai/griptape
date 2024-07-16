import pytest

from griptape.events import CompletionChunkEvent


class TestCompletionChunkEvent:
    @pytest.fixture()
    def completion_chunk_event(self):
        return CompletionChunkEvent(token="foo bar")

    def test_token(self, completion_chunk_event):
        assert completion_chunk_event.token == "foo bar"

    def test_to_dict(self, completion_chunk_event):
        assert completion_chunk_event.to_dict()["token"] == "foo bar"
