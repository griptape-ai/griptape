from griptape.drivers import OllamaEmbeddingDriver

driver = OllamaEmbeddingDriver(
    model="all-minilm",
)

results = driver.embed_string("Hello world!")

# display the first 3 embeddings
print(results[:3])
