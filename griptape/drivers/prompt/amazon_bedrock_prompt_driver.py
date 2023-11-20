from __future__ import annotations
import json
from typing import TYPE_CHECKING, Any, Iterator
from attr import define, field, Factory
from griptape.artifacts import TextArtifact
from griptape.utils import import_optional_dependency, PromptStack
from .base_multi_model_prompt_driver import BaseMultiModelPromptDriver
from griptape.processors import AmazonComprehendPiiProcessor

if TYPE_CHECKING:
    import boto3


@define
class AmazonBedrockPromptDriver(BaseMultiModelPromptDriver):
    session: boto3.Session = field(default=Factory(lambda: import_optional_dependency("boto3").Session()), kw_only=True)
    bedrock_client: Any = field(
        default=Factory(lambda self: self.session.client("bedrock-runtime"), takes_self=True), kw_only=True
    )
    model: str = field(kw_only=True)
    pii_processor: BasePromptStackProcessor = field(default=AmazonComprehendPiiProcessor(), kw_only=True)

    def try_run(self, prompt_stack: PromptStack) -> TextArtifact:
        processed_prompt_stack = self.pii_processor.before_run(prompt_stack)

        model_input = self.prompt_model_driver.prompt_stack_to_model_input(processed_prompt_stack)
        payload = {**self.prompt_model_driver.prompt_stack_to_model_params(processed_prompt_stack)}
        if isinstance(model_input, dict):
            payload.update(model_input)

        response = self.bedrock_client.invoke_model(
            modelId=self.model, contentType="application/json", accept="application/json", body=json.dumps(payload)
        )

        response_body = response["body"].read()

        if response_body:
            result_artifact = self.prompt_model_driver.process_output(response_body)
            processed_result_artifact = self.pii_processor.after_run(result_artifact)
            return processed_result_artifact
        else:
            raise Exception("model response is empty")

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[TextArtifact]:
        processed_prompt_stack = self.pii_processor.before_run(prompt_stack)

        model_input = self.prompt_model_driver.prompt_stack_to_model_input(processed_prompt_stack)
        payload = {**self.prompt_model_driver.prompt_stack_to_model_params(processed_prompt_stack)}
        if isinstance(model_input, dict):
            payload.update(model_input)

        response = self.bedrock_client.invoke_model_with_response_stream(
            modelId=self.model, contentType="application/json", accept="application/json", body=json.dumps(payload)
        )

        response_body = response["body"]
        if response_body:
            for chunk in response["body"]:
                chunk_bytes = chunk["chunk"]["bytes"]
                chunk_artifact = self.prompt_model_driver.process_output(chunk_bytes)
                processed_chunk_artifact = self.pii_processor.after_run(chunk_artifact)
                yield processed_chunk_artifact
        else:
            raise Exception("model response is empty")
