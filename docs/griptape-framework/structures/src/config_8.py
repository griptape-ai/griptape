from griptape.config import config
from griptape.config.drivers import AmazonBedrockDriverConfig
from griptape.structures import Agent

custom_config = AmazonBedrockDriverConfig()
dict_config = custom_config.to_dict()
# Use OpenAi for embeddings
dict_config["embedding_driver"] = {
    "base_url": None,
    "model": "text-embedding-3-small",
    "organization": None,
    "type": "OpenAiEmbeddingDriver",
}
custom_config = AmazonBedrockDriverConfig.from_dict(dict_config)

config.driver_config = custom_config

agent = Agent()
