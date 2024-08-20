from griptape.drivers import GoogleEmbeddingDriver

embeddings = GoogleEmbeddingDriver().embed_string("Hello world!")

# display the first 3 embeddings
print(embeddings[:3])
