from __future__ import annotations
from typing import Iterator, Optional, Any, Literal
import openai
from attr import define, field, Factory
from griptape.artifacts import TextArtifact
from griptape.utils import PromptStack
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import OpenAiTokenizer
from typing import Tuple, Type
import dateparser
from datetime import datetime, timedelta


@define
class OpenAiChatPromptDriver(BasePromptDriver):
    """
    Attributes:
        base_url: An optional OpenAi API URL.
        api_key: An optional OpenAi API key. If not provided, the `OPENAI_API_KEY` environment variable will be used.
        organization: An optional OpenAI organization. If not provided, the `OPENAI_ORG_ID` environment variable will be used.
        client: An `openai.OpenAI` client.
        model: An OpenAI model name.
        tokenizer: An `OpenAiTokenizer`.
        user: A user id. Can be used to track requests by user.
        response_format: An optional OpenAi Chat Completion response format. Currently only supports `json_object` which will enable OpenAi's JSON mode.
        seed: An optional OpenAi Chat Completion seed.
        ignored_exception_types: An optional tuple of exception types to ignore. Defaults to OpenAI's known exception types.
        _ratelimit_request_limit: The maximum number of requests allowed in the current rate limit window.
        _ratelimit_requests_remaining: The number of requests remaining in the current rate limit window.
        _ratelimit_requests_reset_at: The time at which the current rate limit window resets.
        _ratelimit_token_limit: The maximum number of tokens allowed in the current rate limit window.
        _ratelimit_tokens_remaining: The number of tokens remaining in the current rate limit window.
        _ratelimit_tokens_reset_at: The time at which the current rate limit window resets.
    """

    base_url: str | None = field(default=None, kw_only=True)
    api_key: str | None = field(default=None, kw_only=True)
    organization: str | None = field(default=None, kw_only=True)
    client: openai.OpenAI = field(
        default=Factory(
            lambda self: openai.OpenAI(api_key=self.api_key, base_url=self.base_url, organization=self.organization),
            takes_self=True,
        )
    )
    model: str = field(kw_only=True)
    tokenizer: OpenAiTokenizer = field(
        default=Factory(lambda self: OpenAiTokenizer(model=self.model), takes_self=True), kw_only=True
    )
    user: str = field(default="", kw_only=True)
    response_format: Literal["json_object"] | None = field(default=None, kw_only=True)
    seed: int | None = field(default=None, kw_only=True)
    ignored_exception_types: tuple[type[Exception], ...] = field(
        default=Factory(
            lambda: (
                openai.BadRequestError,
                openai.AuthenticationError,
                openai.PermissionDeniedError,
                openai.NotFoundError,
                openai.ConflictError,
                openai.UnprocessableEntityError,
            )
        ),
        kw_only=True,
    )
    _ratelimit_request_limit: int | None = field(init=False, default=None)
    _ratelimit_requests_remaining: int | None = field(init=False, default=None)
    _ratelimit_requests_reset_at: datetime | None = field(init=False, default=None)
    _ratelimit_token_limit: int | None = field(init=False, default=None)
    _ratelimit_tokens_remaining: int | None = field(init=False, default=None)
    _ratelimit_tokens_reset_at: datetime | None = field(init=False, default=None)

    def try_run(self, prompt_stack: PromptStack) -> TextArtifact:
        result = self.client.chat.completions.with_raw_response.create(**self._base_params(prompt_stack))

        self._extract_ratelimit_metadata(result)

        parsed_result = result.parse()
        if len(parsed_result.choices) == 1:
            return TextArtifact(value=parsed_result.choices[0].message.content.strip())
        else:
            raise Exception("Completion with more than one choice is not supported yet.")

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[TextArtifact]:
        result = self.client.chat.completions.create(**self._base_params(prompt_stack), stream=True)

        for chunk in result:
            if len(chunk.choices) == 1:
                delta = chunk.choices[0].delta
            else:
                raise Exception("Completion with more than one choice is not supported yet.")

            if delta.content is not None:
                delta_content = delta.content

                yield TextArtifact(value=delta_content)

    def token_count(self, prompt_stack: PromptStack) -> int:
        return self.tokenizer.count_tokens(self._prompt_stack_to_messages(prompt_stack))

    def _prompt_stack_to_messages(self, prompt_stack: PromptStack) -> list[dict[str, Any]]:
        return [{"role": self.__to_openai_role(i), "content": i.content} for i in prompt_stack.inputs]

    def _base_params(self, prompt_stack: PromptStack) -> dict:
        params = {
            "model": self.model,
            "temperature": self.temperature,
            "stop": self.tokenizer.stop_sequences,
            "user": self.user,
            "seed": self.seed,
        }

        if self.response_format == "json_object":
            params["response_format"] = {"type": "json_object"}
            # JSON mode still requires a system input instructing the LLM to output JSON.
            prompt_stack.add_system_input("Provide your response as a valid JSON object.")

        messages = self._prompt_stack_to_messages(prompt_stack)

        # A max_tokens parameter is not required, but if it is specified by the caller, bound it to
        # the maximum value as determined by the tokenizer and pass it to the API.
        if self.max_tokens:
            params["max_tokens"] = self.max_output_tokens(messages)

        params["messages"] = messages

        return params

    def __to_openai_role(self, prompt_input: PromptStack.Input) -> str:
        if prompt_input.is_system():
            return "system"
        elif prompt_input.is_assistant():
            return "assistant"
        else:
            return "user"

    def _extract_ratelimit_metadata(self, response):
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
                self._ratelimit_requests_reset_at = datetime.now() + timedelta(seconds=1)

        reset_tokens_at = response.headers.get("x-ratelimit-reset-tokens")
        if reset_tokens_at is not None:
            self._ratelimit_tokens_reset_at = dateparser.parse(
                reset_tokens_at, settings={"PREFER_DATES_FROM": "future"}
            )

            if self._ratelimit_tokens_reset_at is None:
                self._ratelimit_tokens_reset_at = datetime.now() + timedelta(seconds=1)

        self._ratelimit_request_limit = response.headers.get("x-ratelimit-limit-requests")
        self._ratelimit_requests_remaining = response.headers.get("x-ratelimit-remaining-requests")
        self._ratelimit_token_limit = response.headers.get("x-ratelimit-limit-tokens")
        self._ratelimit_tokens_remaining = response.headers.get("x-ratelimit-remaining-tokens")
