from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime, timedelta
from typing import Any, Literal, Optional

import dateparser
import openai
from attr import Factory, define, field

from griptape.artifacts import ActionsArtifact, TextArtifact
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import BaseTokenizer, OpenAiTokenizer
from griptape.tools.base_tool import BaseTool
from griptape.utils import PromptStack


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

    base_url: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
    api_key: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": False})
    organization: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": True})
    client: openai.OpenAI = field(
        default=Factory(
            lambda self: openai.OpenAI(api_key=self.api_key, base_url=self.base_url, organization=self.organization),
            takes_self=True,
        )
    )
    model: str = field(kw_only=True, metadata={"serializable": True})
    tokenizer: BaseTokenizer = field(
        default=Factory(lambda self: OpenAiTokenizer(model=self.model), takes_self=True), kw_only=True
    )
    user: str = field(default="", kw_only=True, metadata={"serializable": True})
    response_format: Optional[Literal["json_object"]] = field(
        default=None, kw_only=True, metadata={"serializable": True}
    )
    seed: Optional[int] = field(default=None, kw_only=True, metadata={"serializable": True})
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
    _ratelimit_request_limit: Optional[int] = field(init=False, default=None)
    _ratelimit_requests_remaining: Optional[int] = field(init=False, default=None)
    _ratelimit_requests_reset_at: Optional[datetime] = field(init=False, default=None)
    _ratelimit_token_limit: Optional[int] = field(init=False, default=None)
    _ratelimit_tokens_remaining: Optional[int] = field(init=False, default=None)
    _ratelimit_tokens_reset_at: Optional[datetime] = field(init=False, default=None)

    def try_run(self, prompt_stack: PromptStack) -> TextArtifact:
        result = self.client.chat.completions.with_raw_response.create(**self._base_params(prompt_stack))

        self._extract_ratelimit_metadata(result)

        parsed_result = result.parse()

        if len(parsed_result.choices) == 1:
            message = parsed_result.choices[0].message
            message_content = message.content.strip()

            if message.finish_reason == "tools_call":
                tool_calls = message.tool_calls
                actions = [
                    ActionsArtifact.Action(
                        tag=tool_call.id,
                        name=tool_call.function.name,
                        input=tool_call.function.arguments
                        # TODO: need to add path
                    )
                    for tool_call in tool_calls
                ]

                return ActionsArtifact(value=message_content, actions=actions)
            else:
                # TODO: How do we avoid the final answer of a tools_call going to ActionsSubtask?
                # The LLM will not be following our CoT so there will be no final "Answer:".
                # Maybe we keep this as part of the system prompt.
                return TextArtifact(value=message_content)
        else:
            raise Exception("Completion with more than one choice is not supported yet.")

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[TextArtifact]:
        result = self.client.chat.completions.create(**self._base_params(prompt_stack), stream=True)

        # TODO: function calling with streaming
        for chunk in result:
            if len(chunk.choices) == 1:
                delta = chunk.choices[0].delta
            else:
                raise Exception("Completion with more than one choice is not supported yet.")

            if delta.content is not None:
                delta_content = delta.content

                yield TextArtifact(value=delta_content)

    def token_count(self, prompt_stack: PromptStack) -> int:
        if isinstance(self.tokenizer, OpenAiTokenizer):
            return self.tokenizer.count_tokens(self._prompt_stack_to_messages(prompt_stack))
        else:
            return self.tokenizer.count_tokens(self.prompt_stack_to_string(prompt_stack))

    def _prompt_stack_to_messages(self, prompt_stack: PromptStack) -> list[dict[str, Any]]:
        return [{"role": self.__to_openai_role(i), "content": i.content} for i in prompt_stack.inputs]

    def _base_params(self, prompt_stack: PromptStack) -> dict:
        params = {
            "model": self.model,
            "temperature": self.temperature,
            "stop": self.tokenizer.stop_sequences,
            "user": self.user,
            "seed": self.seed,
            "tools": self.__to_openai_tools(prompt_stack.tools),
        }

        if self.response_format == "json_object":
            params["response_format"] = {"type": "json_object"}
            # JSON mode still requires a system input instructing the LLM to output JSON.
            prompt_stack.add_system_input("Provide your response as a valid JSON object.")

        messages = self._prompt_stack_to_messages(prompt_stack)

        if self.max_tokens is not None:
            params["max_tokens"] = self.max_tokens

        params["messages"] = messages

        return params

    def __to_openai_role(self, prompt_input: PromptStack.Input) -> str:
        if prompt_input.is_system():
            return "system"
        elif prompt_input.is_assistant():
            return "assistant"
        else:
            return "user"

    def __to_openai_tools(self, tools: list[BaseTool]) -> list[dict]:
        return [
            {
                "function": {
                    "name": tool.activity_name(activity),
                    "description": tool.activity_description(activity),
                    "parameters": tool.activity_schema(activity),
                },
                "type": "function",
            }
            for tool in tools
            for activity in tool.activities()
        ]

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
