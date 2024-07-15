from __future__ import annotations

import io
from typing import TYPE_CHECKING, Any

from attrs import Factory, define, field
from schema import Literal, Schema

from griptape.artifacts import BlobArtifact, ErrorArtifact, InfoArtifact, ListArtifact, TextArtifact
from griptape.tools import BaseAwsClient
from griptape.utils.decorators import activity

if TYPE_CHECKING:
    from mypy_boto3_s3 import Client


@define
class AwsS3Client(BaseAwsClient):
    s3_client: Client = field(default=Factory(lambda self: self.session.client("s3"), takes_self=True), kw_only=True)

    @activity(
        config={
            "description": "Can be used to get an access control list (ACL) of an AWS S3 bucket.",
            "schema": Schema(
                {
                    Literal(
                        "bucket_name",
                        description="The bucket name that contains the object for which to get the ACL information.",
                    ): str,
                },
            ),
        },
    )
    def get_bucket_acl(self, params: dict) -> TextArtifact | ErrorArtifact:
        try:
            acl = self.s3_client.get_bucket_acl(Bucket=params["values"]["bucket_name"])
            return TextArtifact(acl)
        except Exception as e:
            return ErrorArtifact(f"error getting bucket acl: {e}")

    @activity(
        config={
            "description": "Can be used to get an AWS S3 bucket policy.",
            "schema": Schema(
                {Literal("bucket_name", description="The bucket name for which to get the bucket policy."): str},
            ),
        },
    )
    def get_bucket_policy(self, params: dict) -> TextArtifact | ErrorArtifact:
        try:
            policy = self.s3_client.get_bucket_policy(Bucket=params["values"]["bucket_name"])
            return TextArtifact(policy)
        except Exception as e:
            return ErrorArtifact(f"error getting bucket policy: {e}")

    @activity(
        config={
            "description": "Can be used to get an access control list (ACL) of an object in the AWS S3 bucket.",
            "schema": Schema(
                {
                    Literal("bucket_name", description="Name of the AWS S3 bucket for which to get an ACL."): str,
                    Literal("object_key", description="Key of the object for which to get the ACL information."): str,
                },
            ),
        },
    )
    def get_object_acl(self, params: dict) -> TextArtifact | ErrorArtifact:
        try:
            acl = self.s3_client.get_object_acl(
                Bucket=params["values"]["bucket_name"],
                Key=params["values"]["object_key"],
            )
            return TextArtifact(acl)
        except Exception as e:
            return ErrorArtifact(f"error getting object acl: {e}")

    @activity(config={"description": "Can be used to list all AWS S3 buckets."})
    def list_s3_buckets(self, _: dict) -> ListArtifact | ErrorArtifact:
        try:
            buckets = self.s3_client.list_buckets()

            return ListArtifact([TextArtifact(str(b)) for b in buckets["Buckets"]])
        except Exception as e:
            return ErrorArtifact(f"error listing s3 buckets: {e}")

    @activity(
        config={
            "description": "Can be used to list all objects in an AWS S3 bucket.",
            "schema": Schema({Literal("bucket_name", description="The name of the S3 bucket to list."): str}),
        },
    )
    def list_objects(self, params: dict) -> ListArtifact | ErrorArtifact:
        try:
            objects = self.s3_client.list_objects_v2(Bucket=params["values"]["bucket_name"])

            if "Contents" not in objects:
                return ErrorArtifact("no objects found in the bucket")

            return ListArtifact([TextArtifact(str(o)) for o in objects["Contents"]])
        except Exception as e:
            return ErrorArtifact(f"error listing objects in bucket: {e}")

    @activity(
        config={
            "description": "Can be used to upload memory artifacts to an AWS S3 bucket",
            "schema": Schema(
                {
                    "memory_name": str,
                    "artifact_namespace": str,
                    "bucket_name": str,
                    Literal("object_key", description="Destination object key name. For example, 'baz.txt'"): str,
                },
            ),
        },
    )
    def upload_memory_artifacts_to_s3(self, params: dict) -> InfoArtifact | ErrorArtifact:
        memory = self.find_input_memory(params["values"]["memory_name"])
        artifact_namespace = params["values"]["artifact_namespace"]
        bucket_name = params["values"]["bucket_name"]
        object_key = params["values"]["object_key"]

        if memory:
            artifacts = memory.load_artifacts(artifact_namespace)

            if len(artifacts) == 0:
                return ErrorArtifact("no artifacts found")
            elif len(artifacts) == 1:
                try:
                    self._upload_object(bucket_name, object_key, artifacts.value[0].value)

                    return InfoArtifact("uploaded successfully")
                except Exception as e:
                    return ErrorArtifact(f"error uploading objects to the bucket: {e}")
            else:
                try:
                    for a in artifacts.value:
                        self._upload_object(bucket_name, object_key, a.value)

                    return InfoArtifact("uploaded successfully")
                except Exception as e:
                    return ErrorArtifact(f"error uploading objects to the bucket: {e}")
        else:
            return ErrorArtifact("memory not found")

    @activity(
        config={
            "description": "Can be used to upload content to an AWS S3 bucket",
            "schema": Schema(
                {
                    "bucket_name": str,
                    Literal("object_key", description="Destination object key name. For example, 'baz.txt'"): str,
                    "content": str,
                },
            ),
        },
    )
    def upload_content_to_s3(self, params: dict) -> ErrorArtifact | InfoArtifact:
        content = params["values"]["content"]
        bucket_name = params["values"]["bucket_name"]
        object_key = params["values"]["object_key"]

        try:
            self._upload_object(bucket_name, object_key, content)

            return InfoArtifact("uploaded successfully")
        except Exception as e:
            return ErrorArtifact(f"error uploading objects to the bucket: {e}")

    @activity(
        config={
            "description": "Can be used to download objects from AWS S3",
            "schema": Schema(
                {
                    Literal("objects", description="A list of bucket name and object key pairs to download"): [
                        {
                            Literal(
                                "bucket_name",
                                description="The name of the bucket to download the object from",
                            ): str,
                            Literal(
                                "object_key",
                                description="The name of the object key to download from the bucket",
                            ): str,
                        },
                    ],
                },
            ),
        },
    )
    def download_objects(self, params: dict) -> ListArtifact | ErrorArtifact:
        objects = params["values"]["objects"]
        artifacts = []
        for object_info in objects:
            try:
                obj = self.s3_client.get_object(Bucket=object_info["bucket_name"], Key=object_info["object_key"])

                content = obj["Body"].read()
                artifacts.append(BlobArtifact(content, name=object_info["object_key"]))

            except Exception as e:
                return ErrorArtifact(f"error downloading objects from bucket: {e}")

        return ListArtifact(artifacts)

    def _upload_object(self, bucket_name: str, object_name: str, value: Any) -> None:
        self.s3_client.create_bucket(Bucket=bucket_name)

        self.s3_client.upload_fileobj(
            Fileobj=io.BytesIO(value.encode() if isinstance(value, str) else value),
            Bucket=bucket_name,
            Key=object_name,
        )
