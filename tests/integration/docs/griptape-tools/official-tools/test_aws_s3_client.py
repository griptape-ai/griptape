class TestAwsS3Client:
    """
    https://docs.griptape.ai/en/latest/griptape-tools/official-tools/aws-s3-client/
    """

    def test_aws_s3_client(self):
        import boto3
        from griptape.tools import AwsS3Client
        from griptape.memory.tool import TextToolMemory

        memory = TextToolMemory()

        client = AwsS3Client(session=boto3.Session(), input_memory=[memory])

        assert client is not None
