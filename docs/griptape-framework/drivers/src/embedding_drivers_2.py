from griptape.drivers import OpenAiEmbeddingDriver

embedding_driver = OpenAiEmbeddingDriver(
    base_url="http://127.0.0.1:1234/v1",
    model="nomic-ai/nomic-embed-text-v1.5-GGUF/nomic-embed-text-v1.5.Q2_K",
)

embeddings = embedding_driver.embed_string("Hello world!")

# display the first 3 embeddings
print(embeddings[:3])
