from griptape.common import TextDeltaMessageContent


class TestTextDeltaMessageContent:
    def test_init(self):
        assert TextDeltaMessageContent("foo").text == "foo"
