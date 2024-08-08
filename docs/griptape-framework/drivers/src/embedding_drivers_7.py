import os

from griptape.drivers import AmazonSageMakerJumpstartEmbeddingDriver

driver = AmazonSageMakerJumpstartEmbeddingDriver(
    model=os.environ["SAGEMAKER_TENSORFLOW_HUB_MODEL"],
)

embeddings = driver.embed_string("Hello world!")

# display the first 3 embeddings
print(embeddings[:3])
