from griptape.drivers.embedding.google import GoogleEmbeddingDriver

embeddings = GoogleEmbeddingDriver().embed("Hello world!")

# display the first 3 embeddings
print(embeddings[:3])
