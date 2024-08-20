from griptape.configs import Defaults
from griptape.configs.drivers import AmazonBedrockDriversConfig
from griptape.structures import Agent

custom_config = AmazonBedrockDriversConfig()
dict_config = custom_config.to_dict()
# Use OpenAi for embeddings
dict_config["embedding_driver"] = {
    "base_url": None,
    "model": "text-embedding-3-small",
    "organization": None,
    "type": "OpenAiEmbeddingDriver",
}
custom_config = AmazonBedrockDriversConfig.from_dict(dict_config)

Defaults.drivers_config = custom_config

agent = Agent()
