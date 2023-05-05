from griptape.rules import Rule


class TestRules:
    def test_init(self):
        rule = Rule("foobar")
        assert rule.value == "foobar"
