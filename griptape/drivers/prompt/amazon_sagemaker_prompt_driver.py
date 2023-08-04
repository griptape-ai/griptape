import json
import boto3
from attr import define, field, Factory
from griptape.artifacts import TextArtifact, ErrorArtifact, BaseArtifact
from griptape.drivers import BasePromptDriver


@define
class AmazonSagemakerPromptDriver(BasePromptDriver):
    endpoint_name: str = field(kw_only=True)
    session: boto3.Session = field(default=boto3.Session())
    sagemaker_client: boto3.client = field(
        default=Factory(
            lambda self: self.session.client("sagemaker-runtime"),
            takes_self=True,
        ),
        kw_only=True,
    )

    def _build_model_input(self, prompt: str) -> any:
        if self.model.startswith("llama"):
            return [
                [
                    {"role": "user", "content": prompt},
                ]
            ]
        elif self.model.startswith("falcon"):
            return prompt
        raise ValueError("unknown model type")

    def _parse_model_output(self, response: any) -> BaseArtifact:
        generations = json.loads(response["Body"].read().decode("utf8"))

        if not generations:
            return ErrorArtifact("no generations from model")

        generation = generations[0]

        if self.model.startswith("llama"):
            return TextArtifact(generation["generation"]["content"])
        elif self.model.startswith("falcon"):
            return TextArtifact(generation["generated_text"])
        else:
            return ErrorArtifact("unknown model type")

    def try_run(self, value: str) -> TextArtifact:
        payload = {
            "inputs": self._build_model_input(value),
            "parameters": {
                "max_new_tokens": self.tokenizer.tokens_left(value),
                "temperature": self.temperature,
            },
        }
        response = self.sagemaker_client.invoke_endpoint(
            EndpointName=self.endpoint_name,
            ContentType="application/json",
            Body=json.dumps(payload),
            CustomAttributes="accept_eula=true",
        )

        return self._parse_model_output(response)
