from griptape.drivers.prompt.minimax import MinimaxPromptDriver
from tests.unit.drivers.prompt.test_openai_chat_prompt_driver import TestOpenAiChatPromptDriverFixtureMixin


class TestMinimaxPromptDriver(TestOpenAiChatPromptDriverFixtureMixin):
    def test_init(self):
        assert MinimaxPromptDriver(api_key="foo", model="MiniMax-M3")

    def test_default_base_url(self):
        driver = MinimaxPromptDriver(api_key="foo", model="MiniMax-M3")

        assert driver.base_url == "https://api.minimax.io/v1"
        assert driver.tokenizer.model == "MiniMax-M3"

    def test_to_dict(self):
        # Given
        driver = MinimaxPromptDriver(model="MiniMax-M3")

        # When
        result = driver.to_dict()

        # Then
        assert result == {
            "type": "MinimaxPromptDriver",
            "audio": {"format": "pcm16", "voice": "alloy"},
            "base_url": "https://api.minimax.io/v1",
            "extra_params": {},
            "max_tokens": None,
            "model": "MiniMax-M3",
            "modalities": [],
            "organization": None,
            "parallel_tool_calls": True,
            "reasoning_effort": "medium",
            "response_format": None,
            "seed": None,
            "stream": False,
            "structured_output_strategy": "native",
            "temperature": 0.1,
            "tokenizer": {
                "type": "MinimaxTokenizer",
                "model": "MiniMax-M3",
                "stop_sequences": [],
            },
            "use_native_tools": True,
            "user": "",
        }

    def test_from_dict(self):
        # Given
        driver = MinimaxPromptDriver(model="MiniMax-M3")

        # When
        result = MinimaxPromptDriver.from_dict(driver.to_dict())

        # Then
        assert result.to_dict() == driver.to_dict()
