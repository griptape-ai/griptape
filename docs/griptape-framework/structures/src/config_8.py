from griptape.config import AmazonBedrockDriverConfig, config
from griptape.structures import Agent

custom_config = AmazonBedrockDriverConfig()
dict_config = custom_config.to_dict()
# Use OpenAi for embeddings
dict_config["embedding"] = {
    "base_url": None,
    "model": "text-embedding-3-small",
    "organization": None,
    "type": "OpenAiEmbeddingDriver",
}
custom_config = AmazonBedrockDriverConfig.from_dict(dict_config)

config.drivers = custom_config

agent = Agent()
