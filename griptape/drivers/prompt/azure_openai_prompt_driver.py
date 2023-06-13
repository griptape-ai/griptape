from attr import define, field, Factory
import openai
from griptape.artifacts import TextArtifact
from griptape.drivers import OpenAiPromptDriver

@define
class AzureOpenAiPromptDriver(OpenAiPromptDriver):
    # This is the Deployment Name. You can find it in the Azure Portal.
    # Azure AI Studio -> Deployments -> Deployment Name
    deployment_id: str = field(kw_only=True)

    # The model is used for token max. It is not passed to Azure OpenAI
    model: str = field(kw_only=True)
    def try_run(self, value: any) -> TextArtifact:
        if self.tokenizer.is_chat():
            return self.__run_chat(value)
        else:
            return self.__run_completion(value)

    def __run_chat(self, value: str) -> TextArtifact:
        result = openai.ChatCompletion.create(
            deployment_id=self.deployment_id,
            messages=[
                {
                    "role": "user",
                    "content": value
                }
            ],
            max_tokens=self.tokenizer.tokens_left(value),
            temperature=self.temperature,
            stop=self.tokenizer.stop_sequence,
            user=self.user
        )

        if len(result.choices) == 1:
            return TextArtifact(
                value=result.choices[0]["message"]["content"].strip()
            )
        else:
            raise Exception("Completion with more than one choice is not supported yet.")

    def __run_completion(self, value: str) -> TextArtifact:
        result = openai.Completion.create(
            deployment_id=self.deployment_id,
            prompt=value,
            max_tokens=self.tokenizer.tokens_left(value),
            temperature=self.temperature,
            stop=self.tokenizer.stop_sequence,
            user=self.user
        )

        if len(result.choices) == 1:
            return TextArtifact(
                value=result.choices[0].text.strip()
            )
        else:
            raise Exception("Completion with more than one choice is not supported yet.")
