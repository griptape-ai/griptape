import os
from typing import Optional
import openai
from attr import define, field, Factory
from griptape.artifacts import TextArtifact
from griptape.utils import PromptStack
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import OpenAiTokenizer
from typing import Tuple, Type
from pytimeparse.timeparse import timeparse
from datetime import datetime, timedelta
import requests


@define
class OpenAiChatPromptDriver(BasePromptDriver):
    """
    Attributes:
        api_type: Can be changed to use OpenAI models on Azure.
        api_version: API version.
        api_base: API URL.
        api_key: API key to pass directly; by default uses `OPENAI_API_KEY_PATH` environment variable.
        max_tokens: Optional maximum return tokens. If not specified, no value will be passed to the API. If set, the
            value will be bounded to the maximum possible as determined by the tokenizer.
        model: OpenAI model name. Uses `gpt-4` by default.
        organization: OpenAI organization.
        tokenizer: Custom `OpenAiTokenizer`.
        user: OpenAI user.
    """

    api_type: str = field(default=openai.api_type, kw_only=True)
    api_version: Optional[str] = field(default=openai.api_version, kw_only=True)
    api_base: str = field(default=openai.api_base, kw_only=True)
    api_key: Optional[str] = field(default=Factory(lambda: os.environ.get("OPENAI_API_KEY")), kw_only=True)
    organization: Optional[str] = field(default=openai.organization, kw_only=True)
    model: str = field(kw_only=True)
    tokenizer: OpenAiTokenizer = field(
        default=Factory(lambda self: OpenAiTokenizer(model=self.model), takes_self=True), kw_only=True
    )
    user: str = field(default="", kw_only=True)
    ignored_exception_types: Tuple[Type[Exception], ...] = field(
        default=Factory(lambda: openai.InvalidRequestError), kw_only=True
    )
    __ratelimit_request_limit: Optional[int] = field(default=None)
    __ratelimit_requests_remaining: Optional[int] = field(default=None)
    __ratelimit_requests_reset_at: Optional[datetime] = field(default=None)
    __ratelimit_token_limit: Optional[int] = field(default=None)
    __ratelimit_tokens_remaining: Optional[int] = field(default=None)
    __ratelimit_tokens_reset_at: Optional[datetime] = field(default=None)

    def try_run(self, prompt_stack: PromptStack) -> TextArtifact:
        # Define a hook to pull rate limit metadata from the OpenAI API response header.
        openai.requestssession = requests.Session()
        openai.requestssession.hooks = {"response": self.__extract_ratelimit_metadata}

        result = openai.ChatCompletion.create(**self._base_params(prompt_stack))

        if len(result.choices) == 1:
            return TextArtifact(value=result.choices[0]["message"]["content"].strip())
        else:
            raise Exception("Completion with more than one choice is not supported yet.")

    def token_count(self, prompt_stack: PromptStack) -> int:
        return self.tokenizer.token_count(self._prompt_stack_to_messages(prompt_stack))

    def _prompt_stack_to_messages(self, prompt_stack: PromptStack) -> list[dict]:
        return [{"role": self.__to_openai_role(i), "content": i.content} for i in prompt_stack.inputs]

    def _base_params(self, prompt_stack: PromptStack) -> dict:
        messages = self._prompt_stack_to_messages(prompt_stack)

        params = {
            "model": self.model,
            "temperature": self.temperature,
            "stop": self.tokenizer.stop_sequences,
            "user": self.user,
            "api_key": self.api_key,
            "organization": self.organization,
            "api_version": self.api_version,
            "api_base": self.api_base,
            "api_type": self.api_type,
            "messages": messages,
        }

        # A max_tokens parameter is not required, but if it is specified by the caller, bound it to
        # the maximum value as determined by the tokenizer and pass it to the API.
        if self.max_tokens:
            params["max_tokens"] = self.max_output_tokens(messages)

        return params

    def __to_openai_role(self, prompt_input: PromptStack.Input) -> str:
        if prompt_input.is_system():
            return "system"
        elif prompt_input.is_assistant():
            return "assistant"
        else:
            return "user"
    @property
    def ratelimit_request_limit(self) -> Optional[int]:
        """Returns the maximum number of requests allowed before the reset time.
        This value is unknown until the first request is made.
        """
        return self.__ratelimit_request_limit

    @property
    def ratelimit_requests_remaining(self) -> Optional[int]:
        """Returns the remaining number of requests allowed before the reset time.
        This value is unknown until the first request is made.
        """
        return self.__ratelimit_requests_remaining

    @property
    def ratelimit_requests_reset_at(self) -> Optional[datetime]:
        """Returns the time at which the request limit will be reset.
        This value is unknown until the first request is made.
        """
        return self.__ratelimit_requests_reset_at

    @property
    def ratelimit_token_limit(self) -> Optional[int]:
        """Returns the maximum number of tokens that may be consumed before the reset time.
        This value is unknown until the first request is made.
        """
        return self.__ratelimit_token_limit

    @property
    def ratelimit_tokens_remaining(self) -> Optional[int]:
        """Returns the remaining number of tokens that may be consumed before the reset time.
        This value is unknown until the first request is made.
        """
        return self.__ratelimit_tokens_remaining

    @property
    def ratelimit_tokens_reset_at(self) -> Optional[datetime]:
        """Returns the time at which the token limit will be reset.
        This value is unknown until the first request is made.
        """
        return self.__ratelimit_tokens_reset_at

    def __extract_ratelimit_metadata(self, response, *args, **kwargs):
        reset_requests_duration_sec = timeparse(response.headers["x-ratelimit-reset-requests-in"])
        self.__ratelimit_request_reset_at = datetime.now() + timedelta(seconds=reset_requests_duration_sec)
        self.__ratelimit_request_limit = response.headers["x-ratelimit-limit-requests"]
        self.__ratelimit_requests_remaining = response.headers["x-ratelimit-remaining-requests"]

        reset_token_duration_sec = timeparse(response.headers["x-ratelimit-reset-tokens-in"])
        self.__ratelimit_token_reset_at = datetime.now() + timedelta(seconds=reset_token_duration_sec)
        self.__ratelimit_token_limit = response.headers["x-ratelimit-limit-tokens"]
        self.__ratelimit_tokens_remaining = response.headers["x-ratelimit-remaining-tokens"]
