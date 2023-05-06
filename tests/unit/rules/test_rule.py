from griptape.rules import Rule


class TestRule:
    def test_init(self):
        rule = Rule("foobar")
        assert rule.value == "foobar"
