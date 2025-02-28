from griptape.drivers.embedding.amazon_bedrock import AmazonBedrockTitanEmbeddingDriver
from griptape.loaders import ImageLoader

embedding_driver = AmazonBedrockTitanEmbeddingDriver()
embeddings = embedding_driver.embed("Hello world!")

print(embeddings[:3])

# Some models support images!
multi_modal_embedding_driver = AmazonBedrockTitanEmbeddingDriver(model="amazon.titan-embed-image-v1")
image = ImageLoader().load("tests/resources/cow.png")
image_embeddings = multi_modal_embedding_driver.embed(image)

print(image_embeddings[:3])
