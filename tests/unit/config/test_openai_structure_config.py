import json
import marshmallow_dataclass
from griptape.config import OpenAiStructureConfig
from griptape.config.base_structure_config import BaseStructureConfig


class TestOpenAiStructureConfig:
    def test_to_dict(self):
        config = OpenAiStructureConfig()
        marshmallow_dataclass.class_schema(OpenAiStructureConfig)().dump(config)

        result = config.to_dict()
        print(json.dumps(result))

        assert result == {
            "type": "OpenAiStructureConfig",
            "prompt_driver": {
                "type": "OpenAiChatPromptDriver",
                "temperature": 0.1,
                "max_tokens": None,
                "model": "gpt-4",
                "stream": False,
            },
        }

        config = BaseStructureConfig.from_dict(result)

        assert config == OpenAiStructureConfig()
