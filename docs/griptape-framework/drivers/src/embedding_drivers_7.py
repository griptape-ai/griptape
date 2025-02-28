import os

from griptape.drivers.embedding.amazon_sagemaker_jumpstart import AmazonSageMakerJumpstartEmbeddingDriver

driver = AmazonSageMakerJumpstartEmbeddingDriver(
    endpoint=os.environ["SAGEMAKER_ENDPOINT"],
    model=os.environ["SAGEMAKER_TENSORFLOW_HUB_MODEL"],
)

embeddings = driver.embed("Hello world!")

# display the first 3 embeddings
print(embeddings[:3])
