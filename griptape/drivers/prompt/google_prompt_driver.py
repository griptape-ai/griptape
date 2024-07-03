from __future__ import annotations

import json
from collections.abc import Iterator
from typing import TYPE_CHECKING, Optional

from attrs import Factory, define, field
from google.generativeai.types import ContentsType

from griptape.common import (
    BaseMessageContent,
    DeltaMessage,
    TextDeltaMessageContent,
    ImageMessageContent,
    PromptStack,
    Message,
    TextMessageContent,
    ActionCallMessageContent,
    ActionResultMessageContent,
    ActionCallDeltaMessageContent,
    BaseDeltaMessageContent,
)
from griptape.artifacts import TextArtifact, ActionArtifact
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import BaseTokenizer, GoogleTokenizer
from griptape.utils import import_optional_dependency, remove_key_in_dict_recursively

if TYPE_CHECKING:
    from google.generativeai import GenerativeModel
    from google.generativeai.types import ContentDict, GenerateContentResponse
    from google.generativeai.protos import Part
    from griptape.tools import BaseTool
    from schema import Schema


@define
class GooglePromptDriver(BasePromptDriver):
    """
    Attributes:
        api_key: Google API key.
        model: Google model name.
        model_client: Custom `GenerativeModel` client.
        top_p: Optional value for top_p.
        top_k: Optional value for top_k.
    """

    api_key: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": False})
    model: str = field(kw_only=True, metadata={"serializable": True})
    model_client: GenerativeModel = field(
        default=Factory(lambda self: self._default_model_client(), takes_self=True), kw_only=True
    )
    tokenizer: BaseTokenizer = field(
        default=Factory(lambda self: GoogleTokenizer(api_key=self.api_key, model=self.model), takes_self=True),
        kw_only=True,
    )
    top_p: Optional[float] = field(default=None, kw_only=True, metadata={"serializable": True})
    top_k: Optional[int] = field(default=None, kw_only=True, metadata={"serializable": True})
    use_native_tools: bool = field(default=True, kw_only=True, metadata={"serializable": True})
    tool_choice: str = field(default="auto", kw_only=True, metadata={"serializable": True})

    def try_run(self, prompt_stack: PromptStack) -> Message:
        messages = self._prompt_stack_to_messages(prompt_stack)
        response: GenerateContentResponse = self.model_client.generate_content(
            messages, **self._base_params(prompt_stack)
        )

        usage_metadata = response.usage_metadata

        return Message(
            content=[self.__google_message_content_to_message_content(part) for part in response.parts],
            role=Message.ASSISTANT_ROLE,
            usage=Message.Usage(
                input_tokens=usage_metadata.prompt_token_count, output_tokens=usage_metadata.candidates_token_count
            ),
        )

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[DeltaMessage]:
        messages = self._prompt_stack_to_messages(prompt_stack)
        response: GenerateContentResponse = self.model_client.generate_content(
            messages, **self._base_params(prompt_stack), stream=True
        )

        prompt_token_count = None
        for chunk in response:
            usage_metadata = chunk.usage_metadata

            content = (
                self.__google_message_content_delta_to_message_content_delta(chunk.parts[0]) if chunk.parts else None
            )
            # Only want to output the prompt token count once since it is static each chunk
            if prompt_token_count is None:
                prompt_token_count = usage_metadata.prompt_token_count
                yield DeltaMessage(
                    content=content,
                    usage=DeltaMessage.Usage(
                        input_tokens=usage_metadata.prompt_token_count,
                        output_tokens=usage_metadata.candidates_token_count,
                    ),
                )
            else:
                yield DeltaMessage(
                    content=content, usage=DeltaMessage.Usage(output_tokens=usage_metadata.candidates_token_count)
                )

    def _base_params(self, prompt_stack: PromptStack) -> dict:
        GenerationConfig = import_optional_dependency("google.generativeai.types").GenerationConfig
        ContentDict = import_optional_dependency("google.generativeai.types").ContentDict
        Part = import_optional_dependency("google.generativeai.protos").Part

        system_messages = prompt_stack.system_messages
        if system_messages:
            self.model_client._system_instruction = ContentDict(
                role="system", parts=[Part(text=system_message.to_text()) for system_message in system_messages]
            )

        return {
            "generation_config": GenerationConfig(
                **{
                    "stop_sequences": []
                    if self.stream
                    and self.use_native_tools  # For some reason, providing stop sequences when streaming breaks native functions
                    else self.tokenizer.stop_sequences,
                    "max_output_tokens": self.max_tokens,
                    "temperature": self.temperature,
                    "top_p": self.top_p,
                    "top_k": self.top_k,
                }
            ),
            **self._prompt_stack_to_tools(prompt_stack),
        }

    def _default_model_client(self) -> GenerativeModel:
        genai = import_optional_dependency("google.generativeai")
        genai.configure(api_key=self.api_key)

        return genai.GenerativeModel(self.model)

    def _prompt_stack_to_messages(self, prompt_stack: PromptStack) -> ContentsType:
        ContentDict = import_optional_dependency("google.generativeai.types").ContentDict

        inputs = [
            ContentDict({"role": self.__to_role(message), "parts": self.__to_content(message)})
            for message in prompt_stack.messages
            if not message.is_system()
        ]

        return inputs

    def _prompt_stack_to_tools(self, prompt_stack: PromptStack) -> dict:
        return (
            {
                "tools": self.__to_tools(prompt_stack.actions),
                "tool_config": {"function_calling_config": {"mode": self.tool_choice}},
            }
            if prompt_stack.actions and self.use_native_tools
            else {}
        )

    def __google_message_content_to_message_content(self, content: Part) -> BaseMessageContent:
        if content.text:
            return TextMessageContent(TextArtifact(content.text))
        elif content.function_call:
            function_call = content.function_call

            name, path = function_call.name.split("_", 1)

            args = {k: v for k, v in function_call.args.items()}
            return ActionCallMessageContent(
                artifact=ActionArtifact(
                    value=ActionArtifact.Action(tag=function_call.name, name=name, path=path, input=args)
                )
            )
        else:
            raise ValueError(f"Unsupported message content type {content}")

    def __prompt_stack_content_message_content(self, content: BaseMessageContent) -> ContentDict | Part | str:
        ContentDict = import_optional_dependency("google.generativeai.types").ContentDict
        protos = import_optional_dependency("google.generativeai.protos")

        if isinstance(content, TextMessageContent):
            return content.artifact.to_text()
        elif isinstance(content, ImageMessageContent):
            return ContentDict(mime_type=content.artifact.mime_type, data=content.artifact.value)
        elif isinstance(content, ActionCallMessageContent):
            action = content.artifact.value

            return protos.Part(function_call=protos.FunctionCall(name=action.tag, args=action.input))
        elif isinstance(content, ActionResultMessageContent):
            artifact = content.artifact

            return protos.Part(
                function_response=protos.FunctionResponse(
                    name=f"{content.action.name}_{content.action.path}", response=artifact.to_dict()
                )
            )

        else:
            raise ValueError(f"Unsupported prompt stack content type: {type(content)}")

    def __google_message_content_delta_to_message_content_delta(self, content: Part) -> BaseDeltaMessageContent:
        if content.text:
            return TextDeltaMessageContent(content.text)
        elif content.function_call:
            function_call = content.function_call

            name, path = function_call.name.split("_", 1)

            args = {k: v for k, v in function_call.args.items()}
            return ActionCallDeltaMessageContent(
                tag=function_call.name, name=name, path=path, partial_input=json.dumps(args)
            )
        else:
            raise ValueError(f"Unsupported message content type {content}")

    def __to_role(self, message: Message) -> str:
        if message.is_assistant():
            return "model"
        else:
            return "user"

    def __to_content(self, message: Message) -> list[ContentDict | str | Part]:
        return [self.__prompt_stack_content_message_content(content) for content in message.content]

    def __to_tools(self, tools: list[BaseTool]) -> list[dict]:
        FunctionDeclaration = import_optional_dependency("google.generativeai.types").FunctionDeclaration

        tool_declarations = []
        for tool in tools:
            for activity in tool.activities():
                schema = (tool.activity_schema(activity) or Schema({})).json_schema("Parameters Schema")["properties"][
                    "values"
                ]

                schema = remove_key_in_dict_recursively(schema, "additionalProperties")
                tool_declaration = FunctionDeclaration(
                    name=f"{tool.name}_{tool.activity_name(activity)}",
                    description=tool.activity_description(activity),
                    parameters={
                        "type": schema["type"],
                        "properties": schema["properties"],
                        "required": schema.get("required", []),
                    },
                )

                tool_declarations.append(tool_declaration)

        return tool_declarations
