import boto3
import pytest

from griptape.tools import AwsS3Client
from tests.utils.aws import mock_aws_credentials


class TestAwsS3Client:
    @pytest.fixture(autouse=True)
    def _run_before_and_after_tests(self):
        mock_aws_credentials()

    def test_get_bucket_acl(self):
        value = {"bucket_name": "bucket_test"}
        assert (
            "error getting bucket acl" in AwsS3Client(session=boto3.Session()).get_bucket_acl({"values": value}).value
        )

    def test_get_bucket_policy(self):
        value = {"bucket_name": "bucket_test"}
        assert (
            "error getting bucket policy"
            in AwsS3Client(session=boto3.Session()).get_bucket_policy({"values": value}).value
        )

    def test_get_object_acl(self):
        value = {"bucket_name": "bucket_test", "object_key": "key_test"}
        assert (
            "error getting object acl" in AwsS3Client(session=boto3.Session()).get_object_acl({"values": value}).value
        )

    def test_list_s3_buckets(self):
        assert "error listing s3 buckets" in AwsS3Client(session=boto3.Session()).list_s3_buckets({}).value

    def test_list_objects(self):
        value = {"bucket_name": "bucket_test"}
        assert (
            "error listing objects in bucket"
            in AwsS3Client(session=boto3.Session()).list_objects({"values": value}).value
        )

    def test_upload_memory_artifacts_to_s3(self):
        value = {
            "memory_name": "foobar",
            "bucket_name": "bucket_test",
            "artifact_namespace": "foo",
            "object_key": "test.txt",
        }
        assert (
            "memory not found"
            in AwsS3Client(session=boto3.Session()).upload_memory_artifacts_to_s3({"values": value}).value
        )

    def test_upload_content_to_s3(self):
        value = {"content": "foobar", "bucket_name": "bucket_test", "object_key": "test.txt"}

        assert (
            "error uploading objects"
            in AwsS3Client(session=boto3.Session()).upload_content_to_s3({"values": value}).value
        )

    def test_download_objects(self):
        value = {"objects": {"bucket_name": "bucket_test", "object_key": "test.txt"}}

        assert (
            "error downloading objects"
            in AwsS3Client(session=boto3.Session()).download_objects({"values": value}).value
        )
