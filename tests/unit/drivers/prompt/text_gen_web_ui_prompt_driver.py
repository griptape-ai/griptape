from transformers import GPT2Tokenizer
from griptape.drivers import TextGenWebUiPromptDriver
from griptape.tokenizers import TextGenTokenizer


class TestTextGenWebUiPromptDriver:
    def test_init(self):
        assert TextGenWebUiPromptDriver(
            tokenizer=TextGenTokenizer(tokenizer=GPT2Tokenizer.from_pretrained("gpt2"))
        )
