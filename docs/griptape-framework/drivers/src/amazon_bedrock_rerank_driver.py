import boto3

from griptape.artifacts import TextArtifact
from griptape.drivers.rerank.amazon_bedrock import AmazonBedrockRerankDriver

rerank_driver = AmazonBedrockRerankDriver(
    session=boto3.Session(region_name="us-east-1"),
    model="cohere.rerank-v3-5:0",
)

artifacts = rerank_driver.run(
    "Where is NYC located?",
    [
        TextArtifact("NYC Media"),
        TextArtifact("New York City Police Department"),
        TextArtifact("New York City"),
        TextArtifact("New York City Subway"),
    ],
)
for artifact in artifacts:
    print(artifact.value)
