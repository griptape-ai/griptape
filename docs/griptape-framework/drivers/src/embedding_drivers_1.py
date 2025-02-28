from griptape.drivers.embedding.openai import OpenAiEmbeddingDriver

embeddings = OpenAiEmbeddingDriver().embed("Hello Griptape!")

# display the first 3 embeddings
print(embeddings[:3])
