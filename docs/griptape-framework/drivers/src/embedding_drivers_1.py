from griptape.drivers import OpenAiEmbeddingDriver

embeddings = OpenAiEmbeddingDriver().embed_string("Hello Griptape!")

# display the first 3 embeddings
print(embeddings[:3])
