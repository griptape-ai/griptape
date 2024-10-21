import pytest

from griptape.events import ActionChunkEvent


class TestCompletionChunkEvent:
    TEST_PARAMS = [
        {"name": "foo", "tag": None, "path": None, "partial_input": None},
        {"name": "foo", "tag": "bar", "path": None, "partial_input": None},
        {"name": "foo", "tag": "bar", "path": "baz", "partial_input": None},
        {"name": "foo", "tag": None, "path": "baz", "partial_input": None},
        {"name": "foo", "tag": "bar", "path": "baz", "partial_input": "qux"},
        {"name": None, "tag": None, "path": None, "partial_input": "qux"},
    ]

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

    def test_to_dict(self, action_chunk_event):
        assert action_chunk_event.to_dict()["partial_input"] == "foo bar"

    @pytest.mark.parametrize("params", TEST_PARAMS)
    def test_str(self, params):
        event = ActionChunkEvent(**params)
        assert str(event) == event.__str__()
