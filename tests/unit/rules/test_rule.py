from griptape.rules import Rule


class TestRule:
    def test_init(self):
        rule = Rule("foobar")
        assert rule.value == "foobar"

    def test_to_text(self):
        rule = Rule("foobar")
        assert rule.to_text() == "foobar"

    def test___str__(self):
        rule = Rule("foobar")
        assert str(rule) == "foobar"
