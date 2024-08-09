from griptape.config import AmazonBedrockStructureConfig
from griptape.drivers import AmazonBedrockCohereEmbeddingDriver
from griptape.structures import Agent

custom_config = AmazonBedrockStructureConfig()
custom_config.embedding_driver = AmazonBedrockCohereEmbeddingDriver()
custom_config.merge_config(
    {
        "embedding_driver": {
            "base_url": None,
            "model": "text-embedding-3-small",
            "organization": None,
            "type": "OpenAiEmbeddingDriver",
        },
    }
)
serialized_config = custom_config.to_json()
deserialized_config = AmazonBedrockStructureConfig.from_json(serialized_config)

agent = Agent(
    config=deserialized_config.merge_config(
        {
            "prompt_driver": {
                "model": "anthropic.claude-3-sonnet-20240229-v1:0",
            },
        }
    ),
)
