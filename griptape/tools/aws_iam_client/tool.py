from __future__ import annotations
from typing import TYPE_CHECKING
from schema import Schema, Literal
from attr import define, field, Factory
from griptape.artifacts import TextArtifact, ErrorArtifact, ListArtifact
from griptape.utils.decorators import activity
from griptape.tools import BaseAwsClient

if TYPE_CHECKING:
    import boto3


@define
class AwsIamClient(BaseAwsClient):
    iam_client: boto3.client = field(
        default=Factory(lambda self: self.session.client("iam"), takes_self=True), kw_only=True
    )

    @activity(
        config={
            "description": "Can be use to get a policy for an AWS IAM user.",
            "schema": Schema(
                {
                    Literal("user_name", description="Username of the AWS IAM user."): str,
                    Literal(
                        "policy_name",
                        description="PolicyName of the AWS IAM Policy embedded in the specified IAM user.",
                    ): str,
                }
            ),
        }
    )
    def get_user_policy(self, params: dict) -> TextArtifact | ErrorArtifact:
        try:
            policy = self.iam_client.get_user_policy(
                UserName=params["values"]["user_name"], PolicyName=params["values"]["policy_name"]
            )
            return TextArtifact(policy["PolicyDocument"])
        except Exception as e:
            return ErrorArtifact(f"error returning policy document: {e}")

    @activity(config={"description": "Can be used to list AWS MFA Devices"})
    def list_mfa_devices(self, _: dict) -> ListArtifact | ErrorArtifact:
        try:
            devices = self.iam_client.list_mfa_devices()
            return ListArtifact([TextArtifact(str(d)) for d in devices["MFADevices"]])
        except Exception as e:
            return ErrorArtifact(f"error listing mfa devices: {e}")

    @activity(
        config={
            "description": "Can be used to list policies for a given IAM user.",
            "schema": Schema(
                {Literal("user_name", description="Username of the AWS IAM user for which to list policies."): str}
            ),
        }
    )
    def list_user_policies(self, params: dict) -> ListArtifact | ErrorArtifact:
        try:
            policies = self.iam_client.list_user_policies(UserName=params["values"]["user_name"])
            policy_names = policies["PolicyNames"]

            attached_policies = self.iam_client.list_attached_user_policies(UserName=params["values"]["user_name"])
            attached_policy_names = [p["PolicyName"] for p in attached_policies["AttachedPolicies"]]

            return ListArtifact([TextArtifact(str(p)) for p in policy_names + attached_policy_names])
        except Exception as e:
            return ErrorArtifact(f"error listing iam user policies: {e}")

    @activity(config={"description": "Can be used to list AWS IAM users."})
    def list_users(self, _: dict) -> ListArtifact | ErrorArtifact:
        try:
            users = self.iam_client.list_users()
            return ListArtifact([TextArtifact(str(u)) for u in users["Users"]])
        except Exception as e:
            return ErrorArtifact(f"error listing s3 users: {e}")
