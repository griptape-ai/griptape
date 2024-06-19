from __future__ import annotations
from typing import TYPE_CHECKING
from collections.abc import Iterator
from attrs import define, field, Factory
from griptape.artifacts import TextArtifact
from griptape.artifacts.list_artifact import ListArtifact
from griptape.common.prompt_stack.contents.delta_action_call_prompt_stack_content import (
    DeltaActionCallPromptStackContent,
)
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import CohereTokenizer
from griptape.artifacts import ActionArtifact
from griptape.common import (
    ActionCallPromptStackContent,
    BaseDeltaPromptStackContent,
    BasePromptStackContent,
    DeltaPromptStackMessage,
    DeltaTextPromptStackContent,
    PromptStack,
    PromptStackMessage,
    TextPromptStackContent,
    ActionResultPromptStackContent,
)
from griptape.utils import import_optional_dependency
from griptape.tokenizers import BaseTokenizer

if TYPE_CHECKING:
    from cohere import Client
    from cohere.types import NonStreamedChatResponse
    from griptape.tools import BaseTool


@define
class CoherePromptDriver(BasePromptDriver):
    """
    Attributes:
        api_key: Cohere API key.
        model: 	Cohere model name.
        client: Custom `cohere.Client`.
    """

    api_key: str = field(kw_only=True, metadata={"serializable": False})
    model: str = field(kw_only=True, metadata={"serializable": True})
    client: Client = field(
        default=Factory(lambda self: import_optional_dependency("cohere").Client(self.api_key), takes_self=True),
        kw_only=True,
    )
    tokenizer: BaseTokenizer = field(
        default=Factory(lambda self: CohereTokenizer(model=self.model, client=self.client), takes_self=True),
        kw_only=True,
    )
    force_single_step: bool = field(default=False, kw_only=True, metadata={"serializable": True})
    tool_choice: dict = field(default=Factory(lambda: {"type": "auto"}), kw_only=True, metadata={"serializable": False})
    use_native_tools: bool = field(default=True, kw_only=True, metadata={"serializable": True})

    def try_run(self, prompt_stack: PromptStack) -> PromptStackMessage:
        result = self.client.chat(**self._base_params(prompt_stack))
        usage = result.meta.tokens

        return PromptStackMessage(
            content=self.__response_to_prompt_stack_content(result),
            role=PromptStackMessage.ASSISTANT_ROLE,
            usage=PromptStackMessage.Usage(input_tokens=usage.input_tokens, output_tokens=usage.output_tokens),
        )

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[DeltaPromptStackMessage]:
        result = self.client.chat_stream(**self._base_params(prompt_stack))

        for event in result:
            if event.event_type == "stream-end":
                usage = event.response.meta.tokens

                return DeltaPromptStackMessage(
                    role=PromptStackMessage.ASSISTANT_ROLE,
                    delta_usage=DeltaPromptStackMessage.DeltaUsage(
                        input_tokens=usage.input_tokens, output_tokens=usage.output_tokens
                    )
                )
            elif event.event_type == "text-generation" or event.event_type == "tool-calls-chunk":
                yield self.__message_delta_to_prompt_stack_content(event.dict())

    def _prompt_stack_messages_to_messages(self, messages: list[PromptStackMessage]) -> list[dict]:
        new_messages = []

        for message in messages:
            new_message: dict = {"role": self.__to_role(message)}

            if message.has_action_results():
                new_message["tool_results"] = [
                    self.__prompt_stack_content_message_content(action_call)
                    for action_call in message.content
                    if isinstance(action_call, ActionResultPromptStackContent)
                ]
            else:
                new_message["message"] = message.to_text_artifact().to_text()
                new_message["tool_calls"] = [
                    self.__prompt_stack_content_message_content(action_call)
                    for action_call in message.content
                    if isinstance(action_call, ActionCallPromptStackContent)
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
        system_element = next((message for message in prompt_stack.messages if message.is_system()), None)
        if system_element is not None:
            if len(system_element.content) == 1:
                preamble = system_element.content[0].artifact.to_text()
            else:
                raise ValueError("System element must have exactly one content.")
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

    def __prompt_stack_content_message_content(self, content: BasePromptStackContent) -> dict:
        if isinstance(content, TextPromptStackContent):
            return {"text": content.artifact.to_text()}
        elif isinstance(content, ActionCallPromptStackContent):
            action = content.artifact.value

            return {"call": {"name": f"{action.name}_{action.path}", "parameters": action.input}}
        elif isinstance(content, ActionResultPromptStackContent):
            artifact = content.artifact

            if isinstance(artifact, ListArtifact):
                message_content = [{"text": artifact.to_text()} for artifact in artifact.value]
            else:
                message_content = [{"text": artifact.to_text()}]

            return {
                "call": {"name": f"{content.action.name}_{content.action.path}", "parameters": content.action.input},
                "outputs": message_content,
            }
        elif isinstance(content, ActionResultPromptStackContent):
            return {"text": content.artifact.to_text()}
        else:
            raise ValueError(f"Unsupported content type: {type(content)}")

    def __response_to_prompt_stack_content(self, response: NonStreamedChatResponse) -> list[BasePromptStackContent]:
        content = []
        if response.text:
            content.append(TextPromptStackContent(TextArtifact(response.text)))
        if response.tool_calls:
            content.extend(
                [
                    ActionCallPromptStackContent(
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

    def __message_delta_to_prompt_stack_content(self, event: dict) -> BaseDeltaPromptStackContent:
        if event["event_type"] == "text-generation":
            return DeltaTextPromptStackContent(event["text"], index=0)
        elif event["event_type"] == "tool-calls-chunk":
            if "tool_call_delta" in event:
                tool_call_delta = event["tool_call_delta"]
                if "name" in tool_call_delta:
                    name, path = tool_call_delta["name"].split("_", 1)

                    return DeltaActionCallPromptStackContent(tag=tool_call_delta["name"], name=name, path=path)
                else:
                    return DeltaActionCallPromptStackContent(delta_input=tool_call_delta["parameters"])

            else:
                return DeltaTextPromptStackContent(event["text"])
        else:
            raise ValueError(f"Unsupported event type: {event['event_type']}")

    def __to_role(self, message: PromptStackMessage) -> str:
        if message.is_system():
            return "SYSTEM"
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
