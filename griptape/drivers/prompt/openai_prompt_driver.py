import json
from typing import Optional
import openai
from attr import define, field, Factory
from griptape.artifacts import TextArtifact
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import TiktokenTokenizer


@define
class OpenAiPromptDriver(BasePromptDriver):
    api_type: str = field(default=openai.api_type, kw_only=True)
    api_version: Optional[str] = field(default=openai.api_version, kw_only=True)
    api_base: str = field(default=openai.api_base, kw_only=True)
    api_key: Optional[str] = field(default=openai.api_key, kw_only=True)
    organization: Optional[str] = field(default=openai.organization, kw_only=True)
    model: str = field(default=TiktokenTokenizer.DEFAULT_MODEL, kw_only=True)
    tokenizer: TiktokenTokenizer = field(
        default=Factory(lambda self: TiktokenTokenizer(model=self.model), takes_self=True),
        kw_only=True
    )
    user: str = field(default="", kw_only=True)

    def __attrs_post_init__(self):
        openai.api_type = self.api_type
        openai.api_version = self.api_version
        openai.api_base = self.api_base
        openai.api_key = self.api_key
        openai.organization = self.organization

    def try_run(self, value: any) -> TextArtifact:
        if self.tokenizer.is_chat():
            return self.__run_chat(value)
        else:
            return self.__run_completion(value)

    def __run_chat(self, value: str) -> TextArtifact:
        result = openai.ChatCompletion.create(
            model=self.tokenizer.model,
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
            model=self.tokenizer.model,
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
