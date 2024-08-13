import os

import boto3

from griptape.config import AmazonBedrockDriverConfig, config
from griptape.structures import Agent

config.drivers = AmazonBedrockDriverConfig(
    session=boto3.Session(
        region_name=os.environ["AWS_DEFAULT_REGION"],
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    )
)

agent = Agent()
