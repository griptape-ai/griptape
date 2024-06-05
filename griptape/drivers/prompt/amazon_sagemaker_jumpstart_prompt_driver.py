from __future__ import annotations
import json
from typing import TYPE_CHECKING, Any
from collections.abc import Iterator
from attrs import define, field, Factory
from griptape.tokenizers import HuggingFaceTokenizer
from griptape.artifacts import TextArtifact
from griptape.drivers.prompt.base_prompt_driver import BasePromptDriver
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    from griptape.utils import PromptStack
    import boto3


@define
class AmazonSageMakerJumpstartPromptDriver(BasePromptDriver):
    session: boto3.Session = field(default=Factory(lambda: import_optional_dependency("boto3").Session()), kw_only=True)
    sagemaker_client: Any = field(
        default=Factory(lambda self: self.session.client("sagemaker-runtime"), takes_self=True), kw_only=True
    )
    endpoint: str = field(kw_only=True, metadata={"serializable": True})
    model: str = field(default=None, kw_only=True, metadata={"serializable": True})
    custom_attributes: str = field(default="accept_eula=true", kw_only=True, metadata={"serializable": True})
    stream: bool = field(default=False, kw_only=True, metadata={"serializable": True})
    max_tokens: int = field(default=250, kw_only=True, metadata={"serializable": True})
    tokenizer: HuggingFaceTokenizer = field(
        default=Factory(
            lambda self: HuggingFaceTokenizer(
                tokenizer=import_optional_dependency("transformers").AutoTokenizer.from_pretrained(self.model),
                max_output_tokens=self.max_tokens,
            ),
            takes_self=True,
        ),
        kw_only=True,
    )

    @stream.validator  # pyright: ignore
    def validate_stream(self, _, stream):
        if stream:
            raise ValueError("streaming is not supported")

    def try_run(self, prompt_stack: PromptStack) -> TextArtifact:
        prompt = self.tokenizer.tokenizer.apply_chat_template(
            [{"role": i.role, "content": i.content} for i in prompt_stack.inputs],
            tokenize=False,
            add_generation_prompt=True,
        )

        payload = {
            "inputs": prompt,
            "parameters": {"temperature": self.temperature, "max_new_tokens": self.max_tokens, "do_sample": True},
        }

        response = self.sagemaker_client.invoke_endpoint(
            EndpointName=self.endpoint,
            ContentType="application/json",
            Body=json.dumps(payload),
            CustomAttributes=self.custom_attributes,
            **({"InferenceComponentName": self.model} if self.model is not None else {}),
        )

        decoded_body = json.loads(response["Body"].read().decode("utf8"))

        if isinstance(decoded_body, list):
            if decoded_body:
                return TextArtifact(decoded_body[0]["generated_text"])
            else:
                raise ValueError("model response is empty")
        else:
            return TextArtifact(decoded_body["generated_text"])

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[TextArtifact]:
        raise NotImplementedError("streaming is not supported")
