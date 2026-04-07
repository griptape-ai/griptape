from griptape.utils import TokenCounter


class TestTokenCounter:
    def test_add_tokens(self):
        counter = TokenCounter()

        counter.add_tokens(5)
        counter.add_tokens(5)

        assert counter.tokens == 10
