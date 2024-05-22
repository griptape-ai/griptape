from __future__ import annotations

import json
from collections.abc import Iterator
from datetime import datetime, timedelta
from typing import Any, Literal, Optional, TYPE_CHECKING

import dateparser
import openai
from attr import Factory, define, field
from schema import Schema

from griptape.artifacts import ActionsArtifact, TextArtifact
from griptape.artifacts.action_chunk_artifact import ActionChunkArtifact
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import BaseTokenizer, OpenAiTokenizer
from griptape.utils import PromptStack
from openai.types.chat.chat_completion_message_tool_call import ChatCompletionMessageToolCall

if TYPE_CHECKING:
    from griptape.tools import BaseTool


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
        function_calling: Whether to use native function calling. Defaults to `True`.
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
    function_calling: bool = field(default=True, kw_only=True, metadata={"serializable": True})
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
            tool_calls: list[ChatCompletionMessageToolCall] = message.tool_calls

            if tool_calls:
                actions = [
                    ActionsArtifact.Action(
                        tag=tool_call.id,
                        name=tool_call.function.name.split("-")[0],
                        path=tool_call.function.name.split("-")[1],
                        input=json.loads(tool_call.function.arguments),
                    )
                    for tool_call in tool_calls
                ]

                return ActionsArtifact(actions=actions)
            else:
                message_content = message.content.strip()

                return TextArtifact(value=message_content)
        else:
            raise Exception("Completion with more than one choice is not supported yet.")

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[TextArtifact]:
        result = self.client.chat.completions.create(**self._base_params(prompt_stack), stream=True)

        for chunk in result:
            if len(chunk.choices) == 1:
                delta = chunk.choices[0].delta
                tool_call_deltas = delta.tool_calls

                if tool_call_deltas:
                    if len(tool_call_deltas) == 1:
                        tool_call_delta = tool_call_deltas[0]

                        if tool_call_delta.id is not None:
                            name, path = tool_call_delta.function.name.split("-")
                            value = f"{name}-{path}"
                        else:
                            name, path = None, None
                            value = tool_call_delta.function.arguments or ""

                        yield ActionChunkArtifact(
                            value=value,
                            index=tool_call_delta.index,
                            tag=tool_call_delta.id,
                            name=name,
                            path=path,
                            partial_input=tool_call_delta.function.arguments,
                        )
                    else:
                        raise Exception("Streaming completion with more than one tool call delta is not supported yet.")
                else:
                    content_delta = delta.content or ""

                    yield TextArtifact(value=content_delta)
            else:
                raise Exception("Completion with more than one choice is not supported yet.")

    def token_count(self, prompt_stack: PromptStack) -> int:
        if isinstance(self.tokenizer, OpenAiTokenizer):
            return self.tokenizer.count_tokens(self._prompt_stack_to_messages(prompt_stack))
        else:
            return self.tokenizer.count_tokens(self.prompt_stack_to_string(prompt_stack))

    def _prompt_stack_to_messages(self, prompt_stack: PromptStack) -> list[dict[str, Any]]:
        messages = []

        for input in prompt_stack.inputs:
            # Each Tool result requires a separate message
            if input.is_tool_result():
                actions_artifact = input.content

                if not isinstance(actions_artifact, ActionsArtifact):
                    raise ValueError("PromptStack Input content must be an ActionsArtifact")

                tool_result_messages = [
                    {
                        "tool_call_id": tool_call.tag,
                        "role": self.__to_openai_role(input),
                        "name": f"{tool_call.name}-{tool_call.path}",
                        "content": tool_call.output.to_text(),
                    }
                    for tool_call in actions_artifact.actions
                ]
                messages.extend(tool_result_messages)
            else:
                if input.is_tool_call():
                    actions_artifact = input.content

                    if not isinstance(actions_artifact, ActionsArtifact):
                        raise ValueError("PromptStack Input content must be an ActionsArtifact")

                    tool_calls = [
                        {
                            "id": action.tag,
                            "function": {"name": f"{action.name}-{action.path}", "arguments": json.dumps(action.input)},
                            "type": "function",
                        }
                        for action in actions_artifact.actions
                    ]
                    message = {"role": self.__to_openai_role(input), "tool_calls": tool_calls}
                else:
                    message = {"role": self.__to_openai_role(input), "content": input.content}

                messages.append(message)

        return messages

    def _prompt_stack_to_tools(self, prompt_stack: PromptStack) -> dict:
        return (
            {"tools": self.__to_openai_tools(prompt_stack.tools)}
            if prompt_stack.tools and self.function_calling
            else {}
        )

    def _base_params(self, prompt_stack: PromptStack) -> dict:
        params = {
            "model": self.model,
            "temperature": self.temperature,
            "stop": self.tokenizer.stop_sequences,
            "user": self.user,
            "seed": self.seed,
            **self._prompt_stack_to_tools(prompt_stack),
            **({"max_tokens": self.max_tokens} if self.max_tokens is not None else {}),
        }

        if self.response_format == "json_object":
            params["response_format"] = {"type": "json_object"}
            # JSON mode still requires a system input instructing the LLM to output JSON.
            prompt_stack.add_system_input("Provide your response as a valid JSON object.")

        messages = self._prompt_stack_to_messages(prompt_stack)

        params["messages"] = messages

        return params

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

    def __to_openai_role(self, prompt_input: PromptStack.Input) -> str:
        if prompt_input.is_system():
            return "system"
        elif prompt_input.is_assistant() or prompt_input.is_tool_call():
            return "assistant"
        elif prompt_input.is_tool_result():
            return "tool"
        else:
            return "user"

    def __to_openai_tools(self, tools: list[BaseTool]) -> list[dict]:
        return [
            {
                "function": {
                    "name": f"{tool.name}-{tool.activity_name(activity)}",
                    "description": tool.activity_description(activity),
                    "parameters": (tool.activity_schema(activity) or Schema({})).json_schema("Parameters Schema"),
                },
                "type": "function",
            }
            for tool in tools
            for activity in tool.activities()
        ]
