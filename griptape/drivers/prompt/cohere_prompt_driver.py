from __future__ import annotations
from typing import TYPE_CHECKING, Any
from collections.abc import Iterator
from attrs import define, field, Factory
from griptape.artifacts import TextArtifact
from griptape.artifacts.list_artifact import ListArtifact
from griptape.common.prompt_stack.contents.action_call_delta_message_content import ActionCallDeltaMessageContent
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import CohereTokenizer
from griptape.artifacts import ActionArtifact
from griptape.common import (
    ActionCallMessageContent,
    BaseDeltaMessageContent,
    BaseMessageContent,
    DeltaMessage,
    TextDeltaMessageContent,
    PromptStack,
    Message,
    TextMessageContent,
    ActionResultMessageContent,
)
from griptape.utils import import_optional_dependency
from griptape.tokenizers import BaseTokenizer

if TYPE_CHECKING:
    from cohere import Client
    from cohere.types import NonStreamedChatResponse
    from griptape.tools import BaseTool


@define(kw_only=True)
class CoherePromptDriver(BasePromptDriver):
    """
    Attributes:
        api_key: Cohere API key.
        model: 	Cohere model name.
        client: Custom `cohere.Client`.
    """

    api_key: str = field(metadata={"serializable": False})
    model: str = field(metadata={"serializable": True})
    client: Client = field(
        default=Factory(lambda self: import_optional_dependency("cohere").Client(self.api_key), takes_self=True)
    )
    tokenizer: BaseTokenizer = field(
        default=Factory(lambda self: CohereTokenizer(model=self.model, client=self.client), takes_self=True)
    )
    force_single_step: bool = field(default=False, kw_only=True, metadata={"serializable": True})
    tool_choice: dict = field(default=Factory(lambda: {"type": "auto"}), kw_only=True, metadata={"serializable": False})
    use_native_tools: bool = field(default=True, kw_only=True, metadata={"serializable": True})

    def try_run(self, prompt_stack: PromptStack) -> Message:
        result = self.client.chat(**self._base_params(prompt_stack))
        usage = result.meta.tokens

        return Message(
            content=self.__response_to_message_content(result),
            role=Message.ASSISTANT_ROLE,
            usage=Message.Usage(input_tokens=usage.input_tokens, output_tokens=usage.output_tokens),
        )

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[DeltaMessage]:
        result = self.client.chat_stream(**self._base_params(prompt_stack))

        for event in result:
            if event.event_type == "stream-end":
                usage = event.response.meta.tokens

                yield DeltaMessage(
                    role=Message.ASSISTANT_ROLE,
                    usage=DeltaMessage.Usage(input_tokens=usage.input_tokens, output_tokens=usage.output_tokens),
                )
            elif event.event_type == "text-generation" or event.event_type == "tool-calls-chunk":
                yield DeltaMessage(content=self.__message_delta_to_message_content(event))

    def _prompt_stack_messages_to_messages(self, messages: list[Message]) -> list[dict]:
        new_messages = []

        for message in messages:
            new_message: dict = {"role": self.__to_role(message)}

            if message.has_action_results():
                new_message["tool_results"] = [
                    self.__prompt_stack_content_message_content(action_call)
                    for action_call in message.content
                    if isinstance(action_call, ActionResultMessageContent)
                ]
            else:
                new_message["message"] = message.to_text()
                if message.has_action_calls():
                    new_message["tool_calls"] = [
                        self.__prompt_stack_content_message_content(action_call)
                        for action_call in message.content
                        if isinstance(action_call, ActionCallMessageContent)
                    ]

            new_messages.append(new_message)

        return new_messages

    def _prompt_stack_to_tools(self, prompt_stack: PromptStack) -> dict:
        return (
            {"tools": self.__to_tools(prompt_stack.actions), "force_single_step": self.force_single_step}
            if prompt_stack.actions and self.use_native_tools
            else {}
        )

    def _base_params(self, prompt_stack: PromptStack) -> dict:
        # Current message
        last_input = prompt_stack.messages[-1]
        user_message = ""
        tool_results = []
        if last_input is not None:
            message = self._prompt_stack_messages_to_messages([prompt_stack.messages[-1]])

            if "message" in message[0]:
                user_message = message[0]["message"]
            elif "tool_results" in message[0]:
                tool_results = message[0]["tool_results"]
            else:
                raise ValueError("Unsupported message type")

        # History messages
        history_messages = self._prompt_stack_messages_to_messages(
            [message for message in prompt_stack.messages[:-1] if not message.is_system()]
        )

        # System message (preamble)
        system_messages = prompt_stack.system_messages
        if system_messages:
            preamble = system_messages[0].to_text()
        else:
            preamble = None

        return {
            "message": user_message,
            "chat_history": history_messages,
            "temperature": self.temperature,
            "stop_sequences": self.tokenizer.stop_sequences,
            "max_tokens": self.max_tokens,
            **({"tool_results": tool_results} if tool_results else {}),
            **self._prompt_stack_to_tools(prompt_stack),
            **({"preamble": preamble} if preamble else {}),
        }

    def __prompt_stack_content_message_content(self, content: BaseMessageContent) -> str | dict:
        if isinstance(content, TextMessageContent):
            return content.artifact.to_text()
        elif isinstance(content, ActionCallMessageContent):
            action = content.artifact.value

            return {"name": f"{action.name}_{action.path}", "parameters": action.input}
        elif isinstance(content, ActionResultMessageContent):
            artifact = content.artifact

            if isinstance(artifact, ListArtifact):
                message_content = [{"text": artifact.to_text()} for artifact in artifact.value]
            else:
                message_content = [{"text": artifact.to_text()}]

            return {
                "call": {"name": f"{content.action.name}_{content.action.path}", "parameters": content.action.input},
                "outputs": message_content,
            }
        elif isinstance(content, ActionResultMessageContent):
            return {"text": content.artifact.to_text()}
        else:
            raise ValueError(f"Unsupported content type: {type(content)}")

    def __response_to_message_content(self, response: NonStreamedChatResponse) -> list[BaseMessageContent]:
        content = []
        if response.text:
            content.append(TextMessageContent(TextArtifact(response.text)))
        if response.tool_calls is not None:
            content.extend(
                [
                    ActionCallMessageContent(
                        ActionArtifact(
                            ActionArtifact.Action(
                                tag=tool_call.name,
                                name=tool_call.name.split("_")[0],
                                path=tool_call.name.split("_")[1],
                                input=tool_call.parameters,
                            )
                        )
                    )
                    for tool_call in response.tool_calls
                ]
            )

        return content

    def __message_delta_to_message_content(self, event: Any) -> BaseDeltaMessageContent:
        if event.event_type == "text-generation":
            return TextDeltaMessageContent(event.text, index=0)
        elif event.event_type == "tool-calls-chunk":
            if event.tool_call_delta is not None:
                tool_call_delta = event.tool_call_delta
                if tool_call_delta.name is not None:
                    name, path = tool_call_delta.name.split("_", 1)

                    return ActionCallDeltaMessageContent(tag=tool_call_delta.name, name=name, path=path)
                else:
                    return ActionCallDeltaMessageContent(partial_input=tool_call_delta.parameters)

            else:
                return TextDeltaMessageContent(event.text)
        else:
            raise ValueError(f"Unsupported event type: {event.event_type}")

    def __to_role(self, message: Message) -> str:
        if message.is_system():
            return "SYSTEM"
        elif message.is_user():
            return "USER"
        elif message.is_assistant():
            return "CHATBOT"
        else:
            if message.has_action_results():
                return "TOOL"
            else:
                return "USER"

    def __to_tools(self, tools: list[BaseTool]) -> list[dict]:
        tool_definitions = []

        for tool in tools:
            for activity in tool.activities():
                properties_values = tool.activity_schema(activity).json_schema("Parameters Schema")["properties"][
                    "values"
                ]
                properties = properties_values["properties"]

                tool_definitions.append(
                    {
                        "name": f"{tool.name}_{tool.activity_name(activity)}",
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
                    }
                )

        return tool_definitions
