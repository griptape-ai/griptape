from __future__ import annotations
import json
from typing import Callable
import boto3
from attr import define, field, Factory
from griptape.artifacts import TextArtifact
from griptape.core import PromptStack
from griptape.drivers import BasePromptDriver


@define
class AmazonSagemakerPromptDriver(BasePromptDriver):
    endpoint_name: str = field(kw_only=True)
    session: boto3.Session = field(default=Factory(lambda: boto3.Session()), kw_only=True)
    sagemaker_client: boto3.client = field(
        default=Factory(
            lambda self: self.session.client("sagemaker-runtime"),
            takes_self=True,
        ),
        kw_only=True,
    )
    build_payload: Callable[[AmazonSagemakerPromptDriver, PromptStack], dict] = field(
        default=Factory(
            lambda self: self.default_payload_builder,
            takes_self=True
        ),
        kw_only=True
    )
    process_output: Callable[[AmazonSagemakerPromptDriver, dict], TextArtifact] = field(
        default=Factory(
            lambda self: self.default_output_processor,
            takes_self=True
        ),
        kw_only=True
    )

    def default_payload_builder(self, driver: AmazonSagemakerPromptDriver, prompt_stack: PromptStack) -> dict:
        prompt = self.prompt_stack_to_string(prompt_stack)

        inputs = {
            "role": "user",
            "content": prompt
        }

        parameters = {
            "max_new_tokens": driver.max_output_tokens(prompt),
            "temperature": driver.temperature,
        }

        return {
            "inputs": inputs,
            "parameters": parameters
        }

    def default_output_processor(self, driver: AmazonSagemakerPromptDriver, output: dict) -> TextArtifact:
        return TextArtifact(str(output))

    def try_run(self, prompt_stack: PromptStack) -> TextArtifact:
        payload = self.build_payload(self, prompt_stack)
        response = self.sagemaker_client.invoke_endpoint(
            EndpointName=self.endpoint_name,
            ContentType="application/json",
            Body=json.dumps(payload),
            CustomAttributes="accept_eula=true",
        )

        generations = json.loads(response["Body"].read().decode("utf8"))

        if generations:
            return self.process_output(self, generations[0])
        else:
            raise Exception("model didn't return any generations")
