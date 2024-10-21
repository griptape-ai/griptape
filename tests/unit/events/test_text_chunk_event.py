import pytest

from griptape.events import TextChunkEvent


class TestCompletionChunkEvent:
    @pytest.fixture()
    def text_chunk_event(self):
        return TextChunkEvent(token="foo bar")

    def test_token(self, text_chunk_event):
        assert text_chunk_event.token == "foo bar"
        assert str(text_chunk_event) == "foo bar"

    def test_to_dict(self, text_chunk_event):
        assert text_chunk_event.to_dict()["token"] == "foo bar"
