from __future__ import annotations

import json
from collections.abc import Iterator
from typing import TYPE_CHECKING, Literal, Optional

import openai
from attrs import Factory, define, field
from schema import Schema

from griptape.artifacts import TextArtifact
from griptape.artifacts.action_call_artifact import ActionCallArtifact
from griptape.common import (
    ActionCallPromptStackContent,
    ActionResultPromptStackContent,
    BaseDeltaPromptStackContent,
    BasePromptStackContent,
    DeltaActionCallPromptStackContent,
    DeltaPromptStackElement,
    DeltaTextPromptStackContent,
    ImagePromptStackContent,
    PromptStack,
    PromptStackMessage,
    TextPromptStackContent,
)
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import BaseTokenizer, OpenAiTokenizer

if TYPE_CHECKING:
    from openai.types.chat.chat_completion_chunk import ChoiceDelta
    from openai.types.chat.chat_completion_message import ChatCompletionMessage

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
    tool_choice: str = field(default="auto", kw_only=True, metadata={"serializable": False})
    use_native_tools: bool = field(default=True, kw_only=True, metadata={"serializable": True})
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

    def try_run(self, prompt_stack: PromptStack) -> PromptStackMessage:
        result = self.client.chat.completions.create(**self._base_params(prompt_stack))

        if len(result.choices) == 1:
            message = result.choices[0].message

            return PromptStackElement(
                content=self.__message_to_prompt_stack_content(message),
                role=PromptStackElement.ASSISTANT_ROLE,
                usage=PromptStackElement.Usage(
                    input_tokens=result.usage.prompt_tokens, output_tokens=result.usage.completion_tokens
                ),
            )
        else:
            raise Exception("Completion with more than one choice is not supported yet.")

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[DeltaPromptStackMessage | BaseDeltaPromptStackContent]:
        result = self.client.chat.completions.create(
            **self._base_params(prompt_stack), stream=True, stream_options={"include_usage": True}
        )

        for chunk in result:
            if chunk.usage is not None:
                yield DeltaPromptStackMessage(
                    delta_usage=DeltaPromptStackMessage.DeltaUsage(
                        input_tokens=chunk.usage.prompt_tokens, output_tokens=chunk.usage.completion_tokens
                    )
                )
            elif chunk.choices is not None:
                if len(chunk.choices) == 1:
                    choice = chunk.choices[0]
                    delta = choice.delta

                    yield self.__message_delta_to_prompt_stack_content_delta(delta)
                else:
                    raise Exception("Completion with more than one choice is not supported yet.")

    def _prompt_stack_to_messages(self, prompt_stack: PromptStack) -> list[dict]:
        messages = []

        for input in prompt_stack.inputs:
            if input.has_action_results():
                # Action results need to be expanded into separate messages.
                for action_result in input.content:
                    if isinstance(action_result, ActionResultPromptStackContent):
                        messages.append(
                            {
                                "role": self.__to_role(input),
                                "content": self.__prompt_stack_content_message_content(action_result),
                                "tool_call_id": action_result.action_tag,
                            }
                        )
            else:
                # Action calls are attached to the assistant message that originally generated them.
                messages.append(
                    {
                        "role": self.__to_role(input),
                        "content": [
                            self.__prompt_stack_content_message_content(content)
                            for content in input.content
                            if not isinstance(  # Action calls do not belong in the content
                                content, ActionCallPromptStackContent
                            )
                        ],
                        **(
                            {
                                "tool_calls": [
                                    self.__prompt_stack_content_message_content(action_call)
                                    for action_call in input.content
                                    if isinstance(action_call, ActionCallPromptStackContent)
                                ]
                            }
                            if input.has_action_calls()
                            else {}
                        ),
                    }
                )

        return messages

    def _prompt_stack_to_tools(self, prompt_stack: PromptStack) -> dict:
        return (
            {"tools": self.__to_tools(prompt_stack.actions), "tool_choice": self.tool_choice}
            if prompt_stack.actions and self.use_native_tools
            else {}
        )

    def _base_params(self, prompt_stack: PromptStack) -> dict:
        params = {
            "model": self.model,
            "temperature": self.temperature,
            "user": self.user,
            "seed": self.seed,
            **self._prompt_stack_to_tools(prompt_stack),
            **({"stop": self.tokenizer.stop_sequences} if self.tokenizer.stop_sequences else {}),
            **({"max_tokens": self.max_tokens} if self.max_tokens is not None else {}),
        }

        if self.response_format == "json_object":
            params["response_format"] = {"type": "json_object"}
            # JSON mode still requires a system input instructing the LLM to output JSON.
            prompt_stack.add_system_message("Provide your response as a valid JSON object.")

        messages = self._prompt_stack_to_messages(prompt_stack)

        params["messages"] = messages

        return params

    def __to_role(self, input: PromptStackMessage) -> str:
        if input.is_system():
            return "system"
        elif input.is_assistant():
            return "assistant"
        else:
            if input.has_action_results():
                return "tool"
            else:
                return "user"

    def __to_tools(self, tools: list[BaseTool]) -> list[dict]:
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

    def __prompt_stack_content_message_content(self, content: BasePromptStackContent) -> str | dict:
        if isinstance(content, TextPromptStackContent):
            return {"type": "text", "text": content.artifact.to_text()}
        elif isinstance(content, ImagePromptStackContent):
            return {
                "type": "image_url",
                "image_url": {"url": f"data:{content.artifact.mime_type};base64,{content.artifact.base64}"},
            }
        elif isinstance(content, ActionCallPromptStackContent):
            action = content.artifact.value

            return {
                "type": "function",
                "id": action.tag,
                "function": {"name": f"{action.name}-{action.path}", "arguments": json.dumps(action.input)},
            }
        elif isinstance(content, ActionResultPromptStackContent):
            return content.artifact.to_text()
        else:
            raise ValueError(f"Unsupported content type: {type(content)}")

    def __message_to_prompt_stack_content(self, message: ChatCompletionMessage) -> list[BasePromptStackContent]:
        if message.content is not None:
            return [TextPromptStackContent(TextArtifact(message.content))]
        elif message.tool_calls is not None:
            return [
                ActionCallPromptStackContent(
                    ActionCallArtifact(
                        ActionCallArtifact.ActionCall(
                            tag=tool_call.id,
                            name=tool_call.function.name.split("-")[0],
                            path=tool_call.function.name.split("-")[1],
                            input=tool_call.function.arguments,
                        )
                    )
                )
                for tool_call in message.tool_calls
            ]
        else:
            raise ValueError(f"Unsupported message type: {message}")

    def __message_delta_to_prompt_stack_content_delta(self, content_delta: ChoiceDelta) -> BaseDeltaPromptStackContent:
        if content_delta.content is not None:
            delta_content = content_delta.content

            return DeltaTextPromptStackContent(delta_content, role=content_delta.role)
        elif content_delta.tool_calls is not None:
            tool_calls = content_delta.tool_calls

            if len(tool_calls) == 1:
                tool_call = tool_calls[0]
                index = tool_call.index

                # Tool call delta either contains the function header or the partial input.
                if tool_call.id is not None:
                    return DeltaActionCallPromptStackContent(
                        index=index,
                        tag=tool_call.id,
                        name=tool_call.function.name.split("-")[0],
                        path=tool_call.function.name.split("-")[1],
                    )
                else:
                    return DeltaActionCallPromptStackContent(index=index, delta_input=tool_call.function.arguments)
            else:
                raise ValueError(f"Unsupported tool call delta length: {len(tool_calls)}")
        else:
            return DeltaTextPromptStackContent("", role=content_delta.role)
