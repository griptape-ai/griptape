class TestAwsIamClient:
    """
    https://docs.griptape.ai/en/latest/griptape-tools/official-tools/aws-iam-client/
    """

    def test_aws_iam_client(self):
        import boto3
        from griptape.tools import AwsIamClient

        client = AwsIamClient(session=boto3.Session())

        assert client is not None
