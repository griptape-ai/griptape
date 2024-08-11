from pathlib import Path

import boto3

from griptape.drivers import AmazonBedrockImageQueryDriver, BedrockClaudeImageQueryModelDriver
from griptape.engines import ImageQueryEngine
from griptape.loaders import ImageLoader

session = boto3.Session(region_name="us-west-2")

driver = AmazonBedrockImageQueryDriver(
    image_query_model_driver=BedrockClaudeImageQueryModelDriver(),
    model="anthropic.claude-3-sonnet-20240229-v1:0",
    session=session,
)

engine = ImageQueryEngine(image_query_driver=driver)

image_artifact = ImageLoader().load(Path("tests/resources/mountain.png").read_bytes())


result = engine.run("Describe the weather in the image", [image_artifact])

print(result)
