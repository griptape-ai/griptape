import os
from typing import Optional
import openai
from attr import define, field, Factory
from griptape.artifacts import TextArtifact
from griptape.core import PromptStack
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import TiktokenTokenizer


@define
class OpenAiPromptDriver(BasePromptDriver):
    api_type: str = field(default=openai.api_type, kw_only=True)
    api_version: Optional[str] = field(default=openai.api_version, kw_only=True)
    api_base: str = field(default=openai.api_base, kw_only=True)
    api_key: Optional[str] = field(default=Factory(lambda: os.environ.get("OPENAI_API_KEY")), kw_only=True)
    organization: Optional[str] = field(default=openai.organization, kw_only=True)
    model: str = field(default=TiktokenTokenizer.DEFAULT_OPENAI_GPT_3_MODEL, kw_only=True)
    tokenizer: TiktokenTokenizer = field(
        default=Factory(lambda self: TiktokenTokenizer(model=self.model), takes_self=True),
        kw_only=True
    )
    user: str = field(default="", kw_only=True)

    def try_run(self, prompt_stack: PromptStack) -> TextArtifact:
        if self.tokenizer.is_chat():
            return self.__run_chat(prompt_stack)
        else:
            return self.__run_completion(prompt_stack)

    def _base_params(self, prompt_stack: PromptStack) -> dict:
        return {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "stop": self.tokenizer.stop_sequences,
            "user": self.user,
            "api_key": self.api_key,
            "organization": self.organization,
            "api_version": self.api_version,
            "api_base": self.api_base,
            "api_type": self.api_type
        }

    def _chat_params(self, prompt_stack: PromptStack) -> dict:
        return self._base_params(prompt_stack) | {
            "messages":  [{"role": i.role, "content": i.content} for i in prompt_stack.inputs]
        }

    def _completion_params(self, prompt_stack: PromptStack) -> dict:
        return self._base_params(prompt_stack) | {
            "prompt": self.default_prompt(prompt_stack),
        }

    def __run_chat(self, prompt_stack: PromptStack) -> TextArtifact:
        result = openai.ChatCompletion.create(**self._chat_params(prompt_stack))

        if len(result.choices) == 1:
            return TextArtifact(
                value=result.choices[0]["message"]["content"].strip()
            )
        else:
            raise Exception("Completion with more than one choice is not supported yet.")

    def __run_completion(self, prompt_stack: PromptStack) -> TextArtifact:
        result = openai.Completion.create(**self._completion_params(prompt_stack))

        if len(result.choices) == 1:
            return TextArtifact(
                value=result.choices[0].text.strip()
            )
        else:
            raise Exception("Completion with more than one choice is not supported yet.")
