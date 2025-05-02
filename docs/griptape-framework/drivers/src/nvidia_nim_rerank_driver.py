from griptape.artifacts import TextArtifact
from griptape.drivers.rerank.nvidia_nim import NvidiaNimRerankDriver

rerank_driver = NvidiaNimRerankDriver(
    model="nvidia/bert-base-uncased",
    base_url="http://localhost:8000",
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
