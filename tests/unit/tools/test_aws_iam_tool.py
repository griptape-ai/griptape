import boto3
import pytest

from griptape.tools import AwsIamTool
from tests.utils.aws import mock_aws_credentials


class TestAwsIamTool:
    @pytest.fixture(autouse=True)
    def _run_before_and_after_tests(self):
        mock_aws_credentials()

    def test_get_user_policy(self):
        value = {"user_name": "test_user", "policy_name": "test_policy"}
        assert (
            "error returning policy document"
            in AwsIamTool(session=boto3.Session()).get_user_policy({"values": value}).value
        )

    def test_list_mfa_devices(self):
        assert "error listing mfa devices" in AwsIamTool(session=boto3.Session()).list_mfa_devices({}).value

    def test_list_user_policies(self):
        value = {"user_name": "test_user"}
        assert (
            "error listing iam user policies"
            in AwsIamTool(session=boto3.Session()).list_user_policies({"values": value}).value
        )

    def test_list_users(self):
        assert "error listing s3 users" in AwsIamTool(session=boto3.Session()).list_users({}).value
