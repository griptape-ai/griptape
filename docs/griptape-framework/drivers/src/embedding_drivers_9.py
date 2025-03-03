import os

from griptape.drivers.embedding.cohere import CohereEmbeddingDriver

embedding_driver = CohereEmbeddingDriver(
    model="embed-english-v3.0",
    api_key=os.environ["COHERE_API_KEY"],
    input_type="search_document",
)

embeddings = embedding_driver.embed("Hello world!")

# display the first 3 embeddings
print(embeddings[:3])
