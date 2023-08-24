from __future__ import annotations
import json
from typing import TYPE_CHECKING, Type
import boto3
from attr import define, field, Factory
from griptape.artifacts import TextArtifact
from griptape.drivers import BasePromptDriver

if TYPE_CHECKING:
    from griptape.core import PromptStack
    from griptape.prompt_model_adapters import BasePromptModelAdapter


@define
class AmazonSagemakerPromptDriver(BasePromptDriver):
    model: str = field(kw_only=True)
    prompt_model_adapter_class: Type[BasePromptModelAdapter] = field(kw_only=True)
    prompt_model_adapter: BasePromptModelAdapter = field(
        default=Factory(lambda self: self.prompt_model_adapter_class(prompt_driver=self), takes_self=True),
        kw_only=True
    )
    session: boto3.Session = field(
        default=Factory(lambda: boto3.Session()),
        kw_only=True
    )
    sagemaker_client: boto3.client = field(
        default=Factory(
            lambda self: self.session.client("sagemaker-runtime"),
            takes_self=True,
        ),
        kw_only=True,
    )
    custom_attributes: str = field(
        default="accept_eula=true",
        kw_only=True
    )

    def try_run(self, prompt_stack: PromptStack) -> TextArtifact:
        payload = {
            "inputs": self.prompt_model_adapter.prompt_stack_to_model_input(prompt_stack),
            "parameters": self.prompt_model_adapter.model_params(prompt_stack)
        }
        response = self.sagemaker_client.invoke_endpoint(
            EndpointName=self.model,
            ContentType="application/json",
            Body=json.dumps(payload),
            CustomAttributes=self.custom_attributes,
        )

        decoded_body = json.loads(response["Body"].read().decode("utf8"))

        if decoded_body:
            return self.prompt_model_adapter.process_output(decoded_body)
        else:
            raise Exception("model response is empty")
