import os
from typing import Optional
import openai
from attr import define, field, Factory
from griptape.artifacts import TextArtifact
from griptape.utils import PromptStack
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import TiktokenTokenizer


@define
class OpenAiChatPromptDriver(BasePromptDriver):
    """
    Attributes:
        api_type: Can be changed to use OpenAI models on Azure.
        api_version: API version. 
        api_base: API URL.
        api_key: API key to pass directly; by default uses `OPENAI_API_KEY_PATH` environment variable.
        max_tokens: Optional maximum return tokens. If not specified, the value will be automatically generated based by the tokenizer.
        model: OpenAI model name. Uses `gpt-4` by default.
        organization: OpenAI organization.
        tokenizer: Custom `TiktokenTokenizer`.
        user: OpenAI user. 	
    """
    api_type: str = field(default=openai.api_type, kw_only=True)
    api_version: Optional[str] = field(default=openai.api_version, kw_only=True)
    api_base: str = field(default=openai.api_base, kw_only=True)
    api_key: Optional[str] = field(default=Factory(lambda: os.environ.get("OPENAI_API_KEY")), kw_only=True)
    organization: Optional[str] = field(default=openai.organization, kw_only=True)
    model: str = field(default=TiktokenTokenizer.DEFAULT_OPENAI_GPT_3_CHAT_MODEL, kw_only=True)
    tokenizer: TiktokenTokenizer = field(
        default=Factory(lambda self: TiktokenTokenizer(model=self.model), takes_self=True),
        kw_only=True
    )
    user: str = field(default="", kw_only=True)

    def try_run(self, prompt_stack: PromptStack) -> TextArtifact:
        result = openai.ChatCompletion.create(**self._base_params(prompt_stack))

        if len(result.choices) == 1:
            return TextArtifact(
                value=result.choices[0]["message"]["content"].strip()
            )
        else:
            raise Exception("Completion with more than one choice is not supported yet.")

    def token_count(self, prompt_stack: PromptStack) -> int:
        return self.tokenizer.token_count(
            self._prompt_stack_to_messages(prompt_stack)
        )

    def max_output_tokens(self, messages: list) -> int:
        if self.max_tokens:
            return self.max_tokens
        else:
            return self.tokenizer.tokens_left(messages)

    def _prompt_stack_to_messages(self, prompt_stack: PromptStack) -> list[dict]:
        return [
            {
                "role": self.__to_openai_role(i),
                "content": i.content
            } for i in prompt_stack.inputs
        ]

    def _base_params(self, prompt_stack: PromptStack) -> dict:
        messages = self._prompt_stack_to_messages(prompt_stack)

        return {
            "model": self.model,
            "max_tokens": self.max_output_tokens(messages),
            "temperature": self.temperature,
            "stop": self.tokenizer.stop_sequences,
            "user": self.user,
            "api_key": self.api_key,
            "organization": self.organization,
            "api_version": self.api_version,
            "api_base": self.api_base,
            "api_type": self.api_type,
            "messages": messages
        }

    def __to_openai_role(self, prompt_input: PromptStack.Input) -> str:
        if prompt_input.is_system():
            return "system"
        elif prompt_input.is_assistant():
            return "assistant"
        else:
            return "user"
