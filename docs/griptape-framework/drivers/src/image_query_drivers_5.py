import boto3

from griptape.drivers import AmazonBedrockImageQueryDriver, BedrockClaudeImageQueryModelDriver
from griptape.loaders import ImageLoader

session = boto3.Session(region_name="us-west-2")

driver = AmazonBedrockImageQueryDriver(
    image_query_model_driver=BedrockClaudeImageQueryModelDriver(),
    model="anthropic.claude-3-sonnet-20240229-v1:0",
    session=session,
)

image_artifact = ImageLoader().load("tests/resources/mountain.png")


result = driver.query("Describe the weather in the image", [image_artifact])

print(result)
