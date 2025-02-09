import os

import boto3

from griptape.drivers.file_manager.amazon_s3 import AmazonS3FileManagerDriver

amazon_s3_file_manager_driver = AmazonS3FileManagerDriver(
    bucket=os.environ["AMAZON_S3_BUCKET"],
    session=boto3.Session(
        region_name=os.environ["AWS_DEFAULT_REGION"],
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
    ),
)

# Download File
file_contents = amazon_s3_file_manager_driver.load_file(os.environ["AMAZON_S3_KEY"])

print(file_contents)

# Upload File
response = amazon_s3_file_manager_driver.save_file(os.environ["AMAZON_S3_KEY"], file_contents.value)

print(response)
