from transformers import GPT2Tokenizer
from griptape.drivers import TextGenPromptDriver
from griptape.tokenizers import TextGenTokenizer


class TestOpenAiPromptDriver:
    def test_init(self):
        assert TextGenPromptDriver(
            tokenizer=TextGenTokenizer(
                tokenizer=GPT2Tokenizer.from_pretrained("gpt2")
            )
        )
