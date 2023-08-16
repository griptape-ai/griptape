from griptape.tools import AwsS3Client
import boto3


class TestAwsS3Client:
    def test_get_bucket_acl(self):
        value = {
            "bucket_name": "bucket_test"
        }
        assert "error getting bucket acl" in AwsS3Client(
            session=boto3.Session()
        ).get_bucket_acl({"values": value}).value

    def test_get_bucket_policy(self):
        value = {
            "bucket_name": "bucket_test"
        }
        assert "error getting bucket policy" in AwsS3Client(
            session=boto3.Session()
        ).get_bucket_policy({"values": value}).value

    def test_get_object_acl(self):
        value = {
            "bucket_name": "bucket_test",
            "object_key": "key_test"
        }
        assert "error getting object acl" in AwsS3Client(
            session=boto3.Session()
        ).get_object_acl({"values": value}).value

    def test_list_s3_buckets(self):
        assert "error listing s3 buckets" in AwsS3Client(
            session=boto3.Session()
        ).list_s3_buckets({}).value

    def test_list_objects(self):
        value = {
            "bucket_name": "bucket_test"
        }
        assert "error listing objects in bucket" in AwsS3Client(
            session=boto3.Session()
        ).list_objects({"values": value}).value

    def test_upload_objects(self):
        value = {
            "memory_id": "foobar",
            "bucket_name": "bucket_test",
            "artifact_namespace": "foo",
            "object_names": [],

        }
        assert "memory not found" in AwsS3Client(
            session=boto3.Session()
        ).upload_objects({"values": value}).value
