import os

from griptape.drivers.embedding.twelvelabs import TwelveLabsEmbeddingDriver

embedding_driver = TwelveLabsEmbeddingDriver(
    model="marengo3.0",
    api_key=os.environ["TWELVELABS_API_KEY"],
)

embeddings = embedding_driver.embed("Hello world!")

# display the first 3 embeddings
print(embeddings[:3])
