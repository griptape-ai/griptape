from __future__ import annotations
import json
from typing import TYPE_CHECKING, Iterator, Any
from attr import define, field, Factory
from griptape.artifacts import TextArtifact
from griptape.utils import import_optional_dependency
from .base_multi_model_prompt_driver import BaseMultiModelPromptDriver
from griptape.processors import AmazonComprehendPiiProcessor

if TYPE_CHECKING:
    from griptape.utils import PromptStack
    import boto3


@define
class AmazonSageMakerPromptDriver(BaseMultiModelPromptDriver):
    session: boto3.Session = field(default=Factory(lambda: import_optional_dependency("boto3").Session()), kw_only=True)
    sagemaker_client: Any = field(
        default=Factory(lambda self: self.session.client("sagemaker-runtime"), takes_self=True), kw_only=True
    )
    custom_attributes: str = field(default="accept_eula=true", kw_only=True)
    stream: bool = field(default=False, kw_only=True)
    pii_processor: AmazonComprehendPiiProcessor = field(default=AmazonComprehendPiiProcessor(), kw_only=True)

    @stream.validator
    def validate_stream(self, _, stream):
        if stream:
            raise ValueError("streaming is not supported")

    def try_run(self, prompt_stack: PromptStack) -> TextArtifact:
        processed_prompt_stack = self.pii_processor.before_run(prompt_stack)
        payload = {
            "inputs": self.prompt_model_driver.prompt_stack_to_model_input(processed_prompt_stack),
            "parameters": self.prompt_model_driver.prompt_stack_to_model_params(processed_prompt_stack),
        }
        response = self.sagemaker_client.invoke_endpoint(
            EndpointName=self.model,
            ContentType="application/json",
            Body=json.dumps(payload),
            CustomAttributes=self.custom_attributes,
        )

        decoded_body = json.loads(response["Body"].read().decode("utf8"))

        if decoded_body:
            result_artifact = self.prompt_model_driver.process_output(decoded_body)
            processed_result_artifact = self.pii_processor.after_run(result_artifact)
            return processed_result_artifact
        else:
            raise Exception("model response is empty")

    def try_stream(self, _: PromptStack) -> Iterator[TextArtifact]:
        raise NotImplementedError("streaming is not supported")
