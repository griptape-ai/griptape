from griptape.drivers.embedding.ollama import OllamaEmbeddingDriver

driver = OllamaEmbeddingDriver(
    model="all-minilm",
)

results = driver.embed("Hello world!")

# display the first 3 embeddings
print(results[:3])
