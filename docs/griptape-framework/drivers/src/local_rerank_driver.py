from griptape.artifacts import TextArtifact
from griptape.drivers.rerank.local import LocalRerankDriver

rerank_driver = LocalRerankDriver()

artifacts = rerank_driver.run(
    "What is the capital of France?",
    [TextArtifact("Hotdog"), TextArtifact("San Francisco"), TextArtifact("Paris")],
)
for artifact in artifacts:
    print(artifact.value)
