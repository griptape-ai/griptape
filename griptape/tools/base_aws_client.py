from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from attrs import define, field

from griptape.artifacts import BaseArtifact, ErrorArtifact, TextArtifact
from griptape.tools import BaseTool
from griptape.utils.decorators import activity

if TYPE_CHECKING:
    import boto3


@define
class BaseAwsClient(BaseTool, ABC):
    session: boto3.Session = field(kw_only=True)

    @activity(config={"description": "Can be used to get current AWS account and IAM principal."})
    def get_current_aws_identity(self, params: dict) -> BaseArtifact:
        try:
            session = self.session
            sts = session.client("sts")
            return TextArtifact(str(sts.get_caller_identity()))
        except Exception as e:
            return ErrorArtifact(f"error getting current aws caller identity: {e}")
