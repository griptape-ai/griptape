from __future__ import annotations

import json
from typing import TYPE_CHECKING, Literal, Optional

import openai
from attrs import Factory, define, field
from schema import Schema

from griptape.artifacts import ActionArtifact, TextArtifact
from griptape.common import (
    ActionCallDeltaMessageContent,
    ActionCallMessageContent,
    ActionResultMessageContent,
    BaseDeltaMessageContent,
    BaseMessageContent,
    DeltaMessage,
    ImageMessageContent,
    Message,
    PromptStack,
    TextDeltaMessageContent,
    TextMessageContent,
    ToolAction,
    observable,
)
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import BaseTokenizer, OpenAiTokenizer

if TYPE_CHECKING:
    from collections.abc import Iterator

    from openai.types.chat.chat_completion_chunk import ChoiceDelta
    from openai.types.chat.chat_completion_message import ChatCompletionMessage

    from griptape.tools import BaseTool


@define
class OpenAiChatPromptDriver(BasePromptDriver):
    """OpenAI Chat Prompt Driver.

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
        ),
    )
    model: str = field(kw_only=True, metadata={"serializable": True})
    tokenizer: BaseTokenizer = field(
        default=Factory(lambda self: OpenAiTokenizer(model=self.model), takes_self=True),
        kw_only=True,
    )
    user: str = field(default="", kw_only=True, metadata={"serializable": True})
    response_format: Optional[Literal["json_object"]] = field(
        default=None,
        kw_only=True,
        metadata={"serializable": True},
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
            ),
        ),
        kw_only=True,
    )

    @observable
    def try_run(self, prompt_stack: PromptStack) -> Message:
        result = self.client.chat.completions.create(**self._base_params(prompt_stack))

        if len(result.choices) == 1:
            message = result.choices[0].message

            return Message(
                content=self.__to_prompt_stack_message_content(message),
                role=Message.ASSISTANT_ROLE,
                usage=Message.Usage(
                    input_tokens=result.usage.prompt_tokens,
                    output_tokens=result.usage.completion_tokens,
                ),
            )
        else:
            raise Exception("Completion with more than one choice is not supported yet.")

    @observable
    def try_stream(self, prompt_stack: PromptStack) -> Iterator[DeltaMessage]:
        result = self.client.chat.completions.create(**self._base_params(prompt_stack), stream=True)

        for chunk in result:
            if chunk.usage is not None:
                yield DeltaMessage(
                    usage=DeltaMessage.Usage(
                        input_tokens=chunk.usage.prompt_tokens,
                        output_tokens=chunk.usage.completion_tokens,
                    ),
                )
            elif chunk.choices is not None:
                if len(chunk.choices) == 1:
                    choice = chunk.choices[0]
                    delta = choice.delta

                    yield DeltaMessage(content=self.__to_prompt_stack_delta_message_content(delta))
                else:
                    raise Exception("Completion with more than one choice is not supported yet.")

    def _base_params(self, prompt_stack: PromptStack) -> dict:
        params = {
            "model": self.model,
            "temperature": self.temperature,
            "user": self.user,
            "seed": self.seed,
            **(
                {"tools": self.__to_openai_tools(prompt_stack.tools), "tool_choice": self.tool_choice}
                if prompt_stack.tools and self.use_native_tools
                else {}
            ),
            **({"stop": self.tokenizer.stop_sequences} if self.tokenizer.stop_sequences else {}),
            **({"max_tokens": self.max_tokens} if self.max_tokens is not None else {}),
            **({"stream_options": {"include_usage": True}} if self.stream else {}),
        }

        if self.response_format == "json_object":
            params["response_format"] = {"type": "json_object"}
            # JSON mode still requires a system message instructing the LLM to output JSON.
            prompt_stack.add_system_message("Provide your response as a valid JSON object.")

        messages = self.__to_openai_messages(prompt_stack.messages)

        params["messages"] = messages

        return params

    def __to_openai_messages(self, messages: list[Message]) -> list[dict]:
        openai_messages = []

        for message in messages:
            # If the message only contains textual content we can send it as a single content.
            if message.is_text():
                openai_messages.append({"role": self.__to_openai_role(message), "content": message.to_text()})
            # Action results must be sent as separate messages.
            elif message.has_any_content_type(ActionResultMessageContent):
                openai_messages.extend(
                    {
                        "role": self.__to_openai_role(message, action_result),
                        "content": self.__to_openai_message_content(action_result),
                        "tool_call_id": action_result.action.tag,
                    }
                    for action_result in message.get_content_type(ActionResultMessageContent)
                )

                if message.has_any_content_type(TextMessageContent):
                    openai_messages.append({"role": self.__to_openai_role(message), "content": message.to_text()})
            else:
                openai_message = {
                    "role": self.__to_openai_role(message),
                    "content": [
                        self.__to_openai_message_content(content)
                        for content in [
                            content for content in message.content if not isinstance(content, ActionCallMessageContent)
                        ]
                    ],
                }

                # Action calls must be attached to the message, not sent as content.
                action_call_content = [
                    content for content in message.content if isinstance(content, ActionCallMessageContent)
                ]
                if action_call_content:
                    openai_message["tool_calls"] = [
                        self.__to_openai_message_content(action_call) for action_call in action_call_content
                    ]

                openai_messages.append(openai_message)

        return openai_messages

    def __to_openai_role(self, message: Message, message_content: Optional[BaseMessageContent] = None) -> str:
        if message.is_system():
            return "system"
        elif message.is_assistant():
            return "assistant"
        else:
            if isinstance(message_content, ActionResultMessageContent):
                return "tool"
            else:
                return "user"

    def __to_openai_tools(self, tools: list[BaseTool]) -> list[dict]:
        return [
            {
                "function": {
                    "name": tool.to_native_tool_name(activity),
                    "description": tool.activity_description(activity),
                    "parameters": (tool.activity_schema(activity) or Schema({})).json_schema("Parameters Schema"),
                },
                "type": "function",
            }
            for tool in tools
            for activity in tool.activities()
        ]

    def __to_openai_message_content(self, content: BaseMessageContent) -> str | dict:
        if isinstance(content, TextMessageContent):
            return {"type": "text", "text": content.artifact.to_text()}
        elif isinstance(content, ImageMessageContent):
            return {
                "type": "image_url",
                "image_url": {"url": f"data:{content.artifact.mime_type};base64,{content.artifact.base64}"},
            }
        elif isinstance(content, ActionCallMessageContent):
            action = content.artifact.value

            return {
                "type": "function",
                "id": action.tag,
                "function": {"name": action.to_native_tool_name(), "arguments": json.dumps(action.input)},
            }
        elif isinstance(content, ActionResultMessageContent):
            return content.artifact.to_text()
        else:
            raise ValueError(f"Unsupported content type: {type(content)}")

    def __to_prompt_stack_message_content(self, response: ChatCompletionMessage) -> list[BaseMessageContent]:
        content = []

        if response.content is not None:
            content.append(TextMessageContent(TextArtifact(response.content)))
        if response.tool_calls is not None:
            content.extend(
                [
                    ActionCallMessageContent(
                        ActionArtifact(
                            ToolAction(
                                tag=tool_call.id,
                                name=ToolAction.from_native_tool_name(tool_call.function.name)[0],
                                path=ToolAction.from_native_tool_name(tool_call.function.name)[1],
                                input=json.loads(tool_call.function.arguments),
                            ),
                        ),
                    )
                    for tool_call in response.tool_calls
                ],
            )

        return content

    def __to_prompt_stack_delta_message_content(self, content_delta: ChoiceDelta) -> BaseDeltaMessageContent:
        if content_delta.content is not None:
            return TextDeltaMessageContent(content_delta.content)
        elif content_delta.tool_calls is not None:
            tool_calls = content_delta.tool_calls

            if len(tool_calls) == 1:
                tool_call = tool_calls[0]
                index = tool_call.index

                # Tool call delta either contains the function header or the partial input.
                if tool_call.id is not None and tool_call.function.name is not None:
                    return ActionCallDeltaMessageContent(
                        index=index,
                        tag=tool_call.id,
                        name=ToolAction.from_native_tool_name(tool_call.function.name)[0],
                        path=ToolAction.from_native_tool_name(tool_call.function.name)[1],
                    )
                else:
                    return ActionCallDeltaMessageContent(index=index, partial_input=tool_call.function.arguments)
            else:
                raise ValueError(f"Unsupported tool call delta length: {len(tool_calls)}")
        else:
            return TextDeltaMessageContent("")
