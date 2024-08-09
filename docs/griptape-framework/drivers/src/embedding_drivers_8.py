import os

from griptape.drivers import VoyageAiEmbeddingDriver

driver = VoyageAiEmbeddingDriver(api_key=os.environ["VOYAGE_API_KEY"])

embeddings = driver.embed_string("Hello world!")

# display the first 3 embeddings
print(embeddings[:3])
