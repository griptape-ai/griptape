import boto3
import pytest
from moto import mock_aws

from griptape.tools import AwsS3Tool


class TestAwsS3Tool:
    @pytest.fixture()
    def session(self):
        mock = mock_aws()
        mock.start()
        yield boto3.Session(region_name="us-east-1")
        mock.stop()

    def test_get_bucket_acl(self, session):
        value = {"bucket_name": "bucket_test"}
        assert "error getting bucket acl" in AwsS3Tool(session=session).get_bucket_acl({"values": value}).value

    def test_get_bucket_policy(self, session):
        value = {"bucket_name": "bucket_test"}
        assert "error getting bucket policy" in AwsS3Tool(session=session).get_bucket_policy({"values": value}).value

    def test_get_object_acl(self, session):
        value = {"bucket_name": "bucket_test", "object_key": "key_test"}
        assert "error getting object acl" in AwsS3Tool(session=session).get_object_acl({"values": value}).value

    def test_list_s3_buckets(self, session):
        assert AwsS3Tool(session=session).list_s3_buckets({}).value == []

    def test_list_objects(self, session):
        value = {"bucket_name": "bucket_test"}
        assert "error listing objects in bucket" in AwsS3Tool(session=session).list_objects({"values": value}).value

    def test_upload_memory_artifacts_to_s3(self, session):
        value = {
            "memory_name": "foobar",
            "bucket_name": "bucket_test",
            "artifact_namespace": "foo",
            "object_key": "test.txt",
        }
        assert "memory not found" in AwsS3Tool(session=session).upload_memory_artifacts_to_s3({"values": value}).value

    def test_upload_content_to_s3(self, session):
        value = {"content": "foobar", "bucket_name": "bucket_test", "object_key": "test.txt"}

        assert "uploaded successfully" in AwsS3Tool(session=session).upload_content_to_s3({"values": value}).value

    def test_download_objects(self, session):
        value = {"objects": {"bucket_name": "bucket_test", "object_key": "test.txt"}}

        assert "error downloading objects" in AwsS3Tool(session=session).download_objects({"values": value}).value
