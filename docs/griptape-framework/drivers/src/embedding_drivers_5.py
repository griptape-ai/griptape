import os

from griptape.drivers.embedding.huggingface_hub import HuggingFaceHubEmbeddingDriver
from griptape.tokenizers import HuggingFaceTokenizer

driver = HuggingFaceHubEmbeddingDriver(
    api_token=os.environ["HUGGINGFACE_HUB_ACCESS_TOKEN"],
    model="sentence-transformers/all-MiniLM-L6-v2",
    tokenizer=HuggingFaceTokenizer(
        model="sentence-transformers/all-MiniLM-L6-v2",
        max_output_tokens=512,
    ),
)

embeddings = driver.embed("Hello world!")

# display the first 3 embeddings
print(embeddings[:3])
