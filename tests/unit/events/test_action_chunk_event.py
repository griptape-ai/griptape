import pytest

from griptape.events import ActionChunkEvent


class TestCompletionChunkEvent:
    @pytest.fixture()
    def action_chunk_event(self):
        return ActionChunkEvent(
            partial_input="foo bar",
            tag="foo",
            name="bar",
            path="baz",
        )

    def test_token(self, action_chunk_event):
        assert action_chunk_event.partial_input == "foo bar"
        assert action_chunk_event.index == 0
        assert action_chunk_event.tag == "foo"
        assert action_chunk_event.name == "bar"
        assert action_chunk_event.path == "baz"
        assert str(action_chunk_event) == "bar.baz (foo) foo bar"

    def test_to_dict(self, action_chunk_event):
        assert action_chunk_event.to_dict()["partial_input"] == "foo bar"
