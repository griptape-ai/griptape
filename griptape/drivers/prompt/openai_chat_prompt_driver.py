from __future__ import annotations
import os
from typing import Iterator, Optional
import openai
from attr import define, field, Factory
from griptape.artifacts import TextArtifact
from griptape.utils import PromptStack
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import OpenAiTokenizer
from typing import Tuple, Type
import dateparser
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
        _ratelimit_request_limit: The maximum number of requests allowed in the current rate limit window.
        _ratelimit_requests_remaining: The number of requests remaining in the current rate limit window.
        _ratelimit_requests_reset_at: The time at which the current rate limit window resets.
        _ratelimit_token_limit: The maximum number of tokens allowed in the current rate limit window.
        _ratelimit_tokens_remaining: The number of tokens remaining in the current rate limit window.
        _ratelimit_tokens_reset_at: The time at which the current rate limit window resets.
    """

    api_type: str = field(default=openai.api_type, kw_only=True)
    api_version: Optional[str] = field(default=openai.api_version, kw_only=True)
    api_base: str = field(default=openai.api_base, kw_only=True)
    api_key: Optional[str] = field(
        default=Factory(lambda: os.environ.get("OPENAI_API_KEY")), kw_only=True
    )
    organization: Optional[str] = field(
        default=openai.organization, kw_only=True
    )
    model: str = field(kw_only=True)
    tokenizer: OpenAiTokenizer = field(
        default=Factory(
            lambda self: OpenAiTokenizer(model=self.model), takes_self=True
        ),
        kw_only=True,
    )
    user: str = field(default="", kw_only=True)
    ignored_exception_types: Tuple[Type[Exception], ...] = field(
        default=Factory(lambda: openai.InvalidRequestError), kw_only=True
    )
    _ratelimit_request_limit: Optional[int] = field(init=False, default=None)
    _ratelimit_requests_remaining: Optional[int] = field(
        init=False, default=None
    )
    _ratelimit_requests_reset_at: Optional[datetime] = field(
        init=False, default=None
    )
    _ratelimit_token_limit: Optional[int] = field(init=False, default=None)
    _ratelimit_tokens_remaining: Optional[int] = field(init=False, default=None)
    _ratelimit_tokens_reset_at: Optional[datetime] = field(
        init=False, default=None
    )

    def __attrs_post_init__(self) -> None:
        # Define a hook to pull rate limit metadata from the OpenAI API response header.
        openai.requestssession = requests.Session()
        openai.requestssession.hooks = {
            "response": self._extract_ratelimit_metadata
        }

    def try_run(self, prompt_stack: PromptStack) -> TextArtifact:
        result = openai.ChatCompletion.create(**self._base_params(prompt_stack))

        if len(result.choices) == 1:
            return TextArtifact(
                value=result.choices[0]["message"]["content"].strip()
            )
        else:
            raise Exception(
                "Completion with more than one choice is not supported yet."
            )

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[TextArtifact]:
        result = openai.ChatCompletion.create(
            **self._base_params(prompt_stack), stream=True
        )

        for chunk in result:
            if len(chunk.choices) == 1:
                delta = chunk.choices[0]["delta"]
            else:
                raise Exception(
                    "Completion with more than one choice is not supported yet."
                )

            if "content" in delta:
                delta_content = delta["content"]

                yield TextArtifact(value=delta_content)

    def token_count(self, prompt_stack: PromptStack) -> int:
        return self.tokenizer.count_tokens(
            self._prompt_stack_to_messages(prompt_stack)
        )

    def _prompt_stack_to_messages(
        self, prompt_stack: PromptStack
    ) -> list[dict]:
        return [
            {"role": self.__to_openai_role(i), "content": i.content}
            for i in prompt_stack.inputs
        ]

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

    def _extract_ratelimit_metadata(self, response, *args, **kwargs):
        # The OpenAI SDK's requestssession variable is global, so this hook will fire for all API requests.
        # The following headers are not reliably returned in every API call, so we check for the presence of the
        # headers before reading and parsing their values to prevent other SDK users from encountering KeyErrors.
        reset_requests_at = response.headers.get("x-ratelimit-reset-requests")
        if reset_requests_at is not None:
            self._ratelimit_requests_reset_at = dateparser.parse(
                reset_requests_at, settings={"PREFER_DATES_FROM": "future"}
            )

            # The dateparser utility doesn't handle sub-second durations as are sometimes returned by OpenAI's API.
            # If the API returns, for example, "13ms", dateparser.parse() returns None. In this case, we will set
            # the time value to the current time plus a one second buffer.
            if self._ratelimit_requests_reset_at is None:
                self._ratelimit_requests_reset_at = datetime.now() + timedelta(
                    seconds=1
                )

        reset_tokens_at = response.headers.get("x-ratelimit-reset-tokens")
        if reset_tokens_at is not None:
            self._ratelimit_tokens_reset_at = dateparser.parse(
                reset_tokens_at, settings={"PREFER_DATES_FROM": "future"}
            )

            if self._ratelimit_tokens_reset_at is None:
                self._ratelimit_tokens_reset_at = datetime.now() + timedelta(
                    seconds=1
                )

        self._ratelimit_request_limit = response.headers.get(
            "x-ratelimit-limit-requests"
        )
        self._ratelimit_requests_remaining = response.headers.get(
            "x-ratelimit-remaining-requests"
        )
        self._ratelimit_token_limit = response.headers.get(
            "x-ratelimit-limit-tokens"
        )
        self._ratelimit_tokens_remaining = response.headers.get(
            "x-ratelimit-remaining-tokens"
        )
