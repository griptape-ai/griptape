from __future__ import annotations

from typing import TYPE_CHECKING, Any

from attrs import Factory, define, field

from griptape.artifacts import ActionArtifact, TextArtifact
from griptape.artifacts.list_artifact import ListArtifact
from griptape.common import (
    ActionCallMessageContent,
    ActionResultMessageContent,
    BaseDeltaMessageContent,
    BaseMessageContent,
    DeltaMessage,
    Message,
    PromptStack,
    TextDeltaMessageContent,
    TextMessageContent,
    ToolAction,
    observable,
)
from griptape.common.prompt_stack.contents.action_call_delta_message_content import ActionCallDeltaMessageContent
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import BaseTokenizer, CohereTokenizer
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    from collections.abc import Iterator

    from cohere import Client
    from cohere.types import NonStreamedChatResponse

    from griptape.tools import BaseTool


@define(kw_only=True)
class CoherePromptDriver(BasePromptDriver):
    """Cohere Prompt Driver.

    Attributes:
        api_key: Cohere API key.
        model: 	Cohere model name.
        client: Custom `cohere.Client`.
    """

    api_key: str = field(metadata={"serializable": False})
    model: str = field(metadata={"serializable": True})
    client: Client = field(
        default=Factory(lambda self: import_optional_dependency("cohere").Client(self.api_key), takes_self=True),
    )
    tokenizer: BaseTokenizer = field(
        default=Factory(lambda self: CohereTokenizer(model=self.model, client=self.client), takes_self=True),
    )
    force_single_step: bool = field(default=False, kw_only=True, metadata={"serializable": True})
    use_native_tools: bool = field(default=True, kw_only=True, metadata={"serializable": True})

    @observable
    def try_run(self, prompt_stack: PromptStack) -> Message:
        result = self.client.chat(**self._base_params(prompt_stack))
        usage = result.meta.tokens

        return Message(
            content=self.__to_prompt_stack_message_content(result),
            role=Message.ASSISTANT_ROLE,
            usage=Message.Usage(input_tokens=usage.input_tokens, output_tokens=usage.output_tokens),
        )

    @observable
    def try_stream(self, prompt_stack: PromptStack) -> Iterator[DeltaMessage]:
        result = self.client.chat_stream(**self._base_params(prompt_stack))

        for event in result:
            if event.event_type == "stream-end":
                usage = event.response.meta.tokens

                yield DeltaMessage(
                    usage=DeltaMessage.Usage(input_tokens=usage.input_tokens, output_tokens=usage.output_tokens),
                )
            elif event.event_type == "text-generation" or event.event_type == "tool-calls-chunk":
                yield DeltaMessage(content=self.__to_prompt_stack_delta_message_content(event))

    def _base_params(self, prompt_stack: PromptStack) -> dict:
        # Current message
        last_input = prompt_stack.messages[-1]
        user_message = ""
        tool_results = []
        if last_input is not None:
            message = self.__to_cohere_messages([prompt_stack.messages[-1]])

            if "message" in message[0]:
                user_message = message[0]["message"]
            if "tool_results" in message[0]:
                tool_results = message[0]["tool_results"]

        # History messages
        history_messages = self.__to_cohere_messages(
            [message for message in prompt_stack.messages[:-1] if not message.is_system()],
        )

        # System message (preamble)
        system_messages = prompt_stack.system_messages
        preamble = system_messages[0].to_text() if system_messages else None

        return {
            "message": user_message,
            "chat_history": history_messages,
            "temperature": self.temperature,
            "stop_sequences": self.tokenizer.stop_sequences,
            "max_tokens": self.max_tokens,
            **({"tool_results": tool_results} if tool_results else {}),
            **(
                {"tools": self.__to_cohere_tools(prompt_stack.tools), "force_single_step": self.force_single_step}
                if prompt_stack.tools and self.use_native_tools
                else {}
            ),
            **({"preamble": preamble} if preamble else {}),
        }

    def __to_cohere_messages(self, messages: list[Message]) -> list[dict]:
        cohere_messages = []

        for message in messages:
            cohere_message: dict = {"role": self.__to_cohere_role(message), "message": message.to_text()}

            if message.has_any_content_type(ActionResultMessageContent):
                cohere_message["tool_results"] = [
                    self.__to_cohere_message_content(action_result)
                    for action_result in message.get_content_type(ActionResultMessageContent)
                ]
            else:
                if message.has_any_content_type(ActionCallMessageContent):
                    cohere_message["tool_calls"] = [
                        self.__to_cohere_message_content(action_call)
                        for action_call in message.get_content_type(ActionCallMessageContent)
                    ]

            cohere_messages.append(cohere_message)

        return cohere_messages

    def __to_cohere_message_content(self, content: BaseMessageContent) -> str | dict:
        if isinstance(content, ActionCallMessageContent):
            action = content.artifact.value

            return {"name": action.to_native_tool_name(), "parameters": action.input}
        elif isinstance(content, ActionResultMessageContent):
            artifact = content.artifact

            if isinstance(artifact, ListArtifact):
                message_content = [{"text": artifact.to_text()} for artifact in artifact.value]
            else:
                message_content = [{"text": artifact.to_text()}]

            return {
                "call": {"name": content.action.to_native_tool_name(), "parameters": content.action.input},
                "outputs": message_content,
            }
        elif isinstance(content, ActionResultMessageContent):
            return {"text": content.artifact.to_text()}
        else:
            raise ValueError(f"Unsupported content type: {type(content)}")

    def __to_cohere_role(self, message: Message) -> str:
        if message.is_system():
            return "SYSTEM"
        elif message.is_assistant():
            return "CHATBOT"
        else:
            if message.has_any_content_type(ActionResultMessageContent):
                return "TOOL"
            else:
                return "USER"

    def __to_cohere_tools(self, tools: list[BaseTool]) -> list[dict]:
        tool_definitions = []

        for tool in tools:
            for activity in tool.activities():
                activity_schema = tool.activity_schema(activity)
                if activity_schema is not None:
                    properties_values = activity_schema.json_schema("Parameters Schema")["properties"]["values"]

                    properties = properties_values["properties"]
                else:
                    properties_values = {}
                    properties = {}

                tool_definitions.append(
                    {
                        "name": tool.to_native_tool_name(activity),
                        "description": tool.activity_description(activity),
                        "parameter_definitions": {
                            property_name: {
                                "type": property_value["type"],
                                "required": property_name in properties_values["required"],
                                **(
                                    {"description": property_value["description"]}
                                    if "description" in property_value
                                    else {}
                                ),
                            }
                            for property_name, property_value in properties.items()
                        },
                    },
                )

        return tool_definitions

    def __to_prompt_stack_message_content(self, response: NonStreamedChatResponse) -> list[BaseMessageContent]:
        content = []
        if response.text:
            content.append(TextMessageContent(TextArtifact(response.text)))
        if response.tool_calls is not None:
            content.extend(
                [
                    ActionCallMessageContent(
                        ActionArtifact(
                            ToolAction(
                                tag=tool_call.name,
                                name=ToolAction.from_native_tool_name(tool_call.name)[0],
                                path=ToolAction.from_native_tool_name(tool_call.name)[1],
                                input=tool_call.parameters,
                            ),
                        ),
                    )
                    for tool_call in response.tool_calls
                ],
            )

        return content

    def __to_prompt_stack_delta_message_content(self, event: Any) -> BaseDeltaMessageContent:
        if event.event_type == "text-generation":
            return TextDeltaMessageContent(event.text, index=0)
        elif event.event_type == "tool-calls-chunk":
            if event.tool_call_delta is not None:
                tool_call_delta = event.tool_call_delta
                if tool_call_delta.name is not None:
                    name, path = ToolAction.from_native_tool_name(tool_call_delta.name)

                    return ActionCallDeltaMessageContent(tag=tool_call_delta.name, name=name, path=path)
                else:
                    return ActionCallDeltaMessageContent(partial_input=tool_call_delta.parameters)

            else:
                return TextDeltaMessageContent(event.text)
        else:
            raise ValueError(f"Unsupported event type: {event.event_type}")
