import boto3

from griptape.structures import Agent
from griptape.tools import AwsS3Client

# Initialize the AWS S3 client
aws_s3_client = AwsS3Client(session=boto3.Session(), off_prompt=True)

# Create an agent with the AWS S3 client tool
agent = Agent(tools=[aws_s3_client])

# Task to list all the AWS S3 buckets
agent.run("List all my S3 buckets.")
