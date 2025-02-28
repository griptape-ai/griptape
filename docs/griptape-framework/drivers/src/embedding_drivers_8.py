import os

from griptape.drivers.embedding.voyageai import VoyageAiEmbeddingDriver
from griptape.loaders import ImageLoader

embedding_driver = VoyageAiEmbeddingDriver(api_key=os.environ["VOYAGE_API_KEY"])
embeddings = embedding_driver.embed("Hello world!")

print(embeddings[:3])

# Some models support images!
multi_modal_embedding_driver = VoyageAiEmbeddingDriver(
    api_key=os.environ["VOYAGE_API_KEY"], model="voyage-multimodal-3"
)
image = ImageLoader().load("tests/resources/cow.png")
image_embeddings = multi_modal_embedding_driver.embed(image)

print(image_embeddings[:3])
