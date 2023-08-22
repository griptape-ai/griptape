import json
import boto3
from attr import define, field, Factory
from griptape.artifacts import TextArtifact, ErrorArtifact, BaseArtifact
from griptape.drivers import BasePromptDriver
from griptape.core import PromptStack


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

    def _build_model_input(self, prompt_stack: PromptStack) -> any:
        if self.model.startswith("llama"):
            return [
                {"role": prompt_line.role, "content": prompt_line.content}
                for prompt_line in prompt_stack.inputs
            ]
        elif self.model.startswith("falcon"):
            # https://huggingface.co/tiiuae/falcon-7b-instruct/discussions/1
            prompt_lines = []

            for i in prompt_stack.inputs:
                if i.is_assistant():
                    prompt_lines.append(f"Assistant: {i.content}")
                elif i.is_user():
                    prompt_lines.append(f"User: {i.content}")
                elif i.is_system():
                    prompt_lines.append(f"Context: {i.content}")

            prompt_lines.append("Assistant:")

            prompt = "\n\n" + "\n\n".join(prompt_lines)

            return prompt
        raise ValueError("unknown model type")

    def _build_model_parameters(self, prompt: str) -> any:
        parameters = {
            "max_new_tokens": self.tokenizer.tokens_left(prompt),
            "temperature": self.temperature,
        }
        if self.model.startswith("falcon"):
            parameters["stop"] = self.tokenizer.stop_sequences
        return parameters

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

    def try_run(self, prompt_stack: PromptStack) -> TextArtifact:
        payload = {
            "inputs": self._build_model_input(prompt_stack),
            "parameters": self._build_model_parameters(prompt_stack),
        }
        response = self.sagemaker_client.invoke_endpoint(
            EndpointName=self.endpoint_name,
            ContentType="application/json",
            Body=json.dumps(payload),
            CustomAttributes="accept_eula=true",
        )

        return self._parse_model_output(response)
