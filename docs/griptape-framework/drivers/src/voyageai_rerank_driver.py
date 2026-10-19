import os

from griptape.artifacts import TextArtifact
from griptape.drivers.rerank.voyageai import VoyageAiRerankDriver

rerank_driver = VoyageAiRerankDriver(
    api_key=os.environ["VOYAGE_API_KEY"],
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
