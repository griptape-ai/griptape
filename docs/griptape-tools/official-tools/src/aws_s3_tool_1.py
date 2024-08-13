import boto3

from griptape.structures import Agent
from griptape.tools import AwsS3Tool, TaskMemoryTool

# Initialize the AWS S3 client
aws_s3_client = AwsS3Tool(session=boto3.Session(), off_prompt=True)

# Create an agent with the AWS S3 client tool
agent = Agent(tools=[aws_s3_client, TaskMemoryTool(off_prompt=False)])

# Task to list all the AWS S3 buckets
agent.run("List all my S3 buckets.")
