from griptape.config import OpenAiStructureConfig


class TestOpenAiStructureConfig:
    def test_to_dict(self):
        config = OpenAiStructureConfig()

        result = config.to_dict()

        assert result == {
            "args": {
                "engine": "davinci",
                "max_tokens": 64,
                "temperature": 0.7,
                "top_p": 1.0,
                "frequency_penalty": 0.0,
                "presence_penalty": 0.0,
                "stop": ["\n"],
            }
        }
