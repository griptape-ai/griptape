import pytest

from griptape.artifacts.video_url_artifact import VideoUrlArtifact
from griptape.common import PromptStack
from griptape.drivers.prompt.minimax import MinimaxPromptDriver
from tests.unit.drivers.prompt.test_openai_chat_prompt_driver import TestOpenAiChatPromptDriverFixtureMixin


class TestMinimaxPromptDriver(TestOpenAiChatPromptDriverFixtureMixin):
    @pytest.mark.parametrize("model", ["MiniMax-M3.1-Flash", "MiniMax-M3", "custom-model"])
    def test_init(self, model):
        assert MinimaxPromptDriver(api_key="foo", model=model)

    def test_default_base_url(self):
        driver = MinimaxPromptDriver(api_key="foo")

        assert driver.base_url == "https://api.minimax.io/v1"
        assert driver.model == "MiniMax-M3.1-Flash"
        assert driver.tokenizer.model == driver.model
        assert "reasoning_effort" not in driver._base_params(PromptStack())

    @pytest.mark.parametrize("effort", ["low", "medium", "high", "xhigh", "max"])
    def test_flash_thinking_params(self, effort):
        driver = MinimaxPromptDriver(
            api_key="foo",
            extra_params={"reasoning_effort": effort, "extra_body": {"thinking": {"type": "adaptive"}}},
        )

        params = driver._base_params(PromptStack())

        assert params["reasoning_effort"] == effort
        assert params["extra_body"] == {"thinking": {"type": "adaptive"}}
        assert MinimaxPromptDriver.from_dict(driver.to_dict()).extra_params == driver.extra_params

    @pytest.mark.parametrize("thinking", ["adaptive", "disabled"])
    def test_m3_thinking_params(self, thinking):
        driver = MinimaxPromptDriver(
            api_key="foo",
            model="MiniMax-M3",
            extra_params={"extra_body": {"thinking": {"type": thinking}}},
        )

        params = driver._base_params(PromptStack())

        assert params["extra_body"] == {"thinking": {"type": thinking}}
        assert "reasoning_effort" not in params

    @pytest.mark.parametrize("model", ["MiniMax-M3.1-Flash", "MiniMax-M3"])
    def test_video_input(self, model):
        driver = MinimaxPromptDriver(api_key="foo", model=model)
        prompt_stack = PromptStack()
        prompt_stack.add_user_message(VideoUrlArtifact("https://example.com/video.mp4"))

        params = driver._base_params(prompt_stack)

        assert params["messages"][0]["content"] == [
            {"type": "video_url", "video_url": {"url": "https://example.com/video.mp4"}}
        ]

    def test_custom_base_url(self):
        driver = MinimaxPromptDriver(
            api_key="foo",
            model="MiniMax-M3",
            base_url="https://api.minimaxi.com/v1",
        )

        assert driver.base_url == "https://api.minimaxi.com/v1"

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
