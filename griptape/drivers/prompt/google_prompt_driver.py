from __future__ import annotations

import json
from typing import TYPE_CHECKING, Optional

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
    GenericMessageContent,
    ImageMessageContent,
    Message,
    PromptStack,
    TextDeltaMessageContent,
    TextMessageContent,
    ToolAction,
    observable,
)
from griptape.drivers import BasePromptDriver
from griptape.tokenizers import BaseTokenizer, GoogleTokenizer
from griptape.utils import import_optional_dependency, remove_key_in_dict_recursively

if TYPE_CHECKING:
    from collections.abc import Iterator

    from google.generativeai import GenerativeModel
    from google.generativeai.protos import Part
    from google.generativeai.types import ContentDict, ContentsType, GenerateContentResponse

    from griptape.tools import BaseTool


@define
class GooglePromptDriver(BasePromptDriver):
    """Google Prompt Driver.

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
        default=Factory(lambda self: self._default_model_client(), takes_self=True),
        kw_only=True,
    )
    tokenizer: BaseTokenizer = field(
        default=Factory(lambda self: GoogleTokenizer(api_key=self.api_key, model=self.model), takes_self=True),
        kw_only=True,
    )
    top_p: Optional[float] = field(default=None, kw_only=True, metadata={"serializable": True})
    top_k: Optional[int] = field(default=None, kw_only=True, metadata={"serializable": True})
    use_native_tools: bool = field(default=True, kw_only=True, metadata={"serializable": True})
    tool_choice: str = field(default="auto", kw_only=True, metadata={"serializable": True})

    @observable
    def try_run(self, prompt_stack: PromptStack) -> Message:
        messages = self.__to_google_messages(prompt_stack)
        response: GenerateContentResponse = self.model_client.generate_content(
            messages,
            **self._base_params(prompt_stack),
        )

        usage_metadata = response.usage_metadata

        return Message(
            content=[self.__to_prompt_stack_message_content(part) for part in response.parts],
            role=Message.ASSISTANT_ROLE,
            usage=Message.Usage(
                input_tokens=usage_metadata.prompt_token_count,
                output_tokens=usage_metadata.candidates_token_count,
            ),
        )

    @observable
    def try_stream(self, prompt_stack: PromptStack) -> Iterator[DeltaMessage]:
        messages = self.__to_google_messages(prompt_stack)
        response: GenerateContentResponse = self.model_client.generate_content(
            messages,
            **self._base_params(prompt_stack),
            stream=True,
        )

        prompt_token_count = None
        for chunk in response:
            usage_metadata = chunk.usage_metadata

            content = self.__to_prompt_stack_delta_message_content(chunk.parts[0]) if chunk.parts else None
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
                    content=content,
                    usage=DeltaMessage.Usage(output_tokens=usage_metadata.candidates_token_count),
                )

    def _base_params(self, prompt_stack: PromptStack) -> dict:
        types = import_optional_dependency("google.generativeai.types")
        protos = import_optional_dependency("google.generativeai.protos")

        system_messages = prompt_stack.system_messages
        if system_messages:
            self.model_client._system_instruction = types.ContentDict(
                role="system",
                parts=[protos.Part(text=system_message.to_text()) for system_message in system_messages],
            )

        return {
            "generation_config": types.GenerationConfig(
                **{
                    # For some reason, providing stop sequences when streaming breaks native functions
                    # https://github.com/google-gemini/generative-ai-python/issues/446
                    "stop_sequences": [] if self.stream and self.use_native_tools else self.tokenizer.stop_sequences,
                    "max_output_tokens": self.max_tokens,
                    "temperature": self.temperature,
                    "top_p": self.top_p,
                    "top_k": self.top_k,
                },
            ),
            **(
                {
                    "tools": self.__to_google_tools(prompt_stack.tools),
                    "tool_config": {"function_calling_config": {"mode": self.tool_choice}},
                }
                if prompt_stack.tools and self.use_native_tools
                else {}
            ),
        }

    def _default_model_client(self) -> GenerativeModel:
        genai = import_optional_dependency("google.generativeai")
        genai.configure(api_key=self.api_key)

        return genai.GenerativeModel(self.model)

    def __to_google_messages(self, prompt_stack: PromptStack) -> ContentsType:
        types = import_optional_dependency("google.generativeai.types")

        inputs = [
            types.ContentDict(
                {
                    "role": self.__to_google_role(message),
                    "parts": [self.__to_google_message_content(content) for content in message.content],
                },
            )
            for message in prompt_stack.messages
            if not message.is_system()
        ]

        return inputs

    def __to_google_role(self, message: Message) -> str:
        if message.is_assistant():
            return "model"
        else:
            return "user"

    def __to_google_tools(self, tools: list[BaseTool]) -> list[dict]:
        types = import_optional_dependency("google.generativeai.types")

        tool_declarations = []
        for tool in tools:
            for activity in tool.activities():
                schema = (tool.activity_schema(activity) or Schema({})).json_schema("Parameters Schema")

                if "values" in schema["properties"]:
                    schema = schema["properties"]["values"]

                schema = remove_key_in_dict_recursively(schema, "additionalProperties")
                tool_declaration = types.FunctionDeclaration(
                    name=tool.to_native_tool_name(activity),
                    description=tool.activity_description(activity),
                    parameters={
                        "type": schema["type"],
                        "properties": schema["properties"],
                        "required": schema.get("required", []),
                    },
                )

                tool_declarations.append(tool_declaration)

        return tool_declarations

    def __to_google_message_content(self, content: BaseMessageContent) -> ContentDict | Part | str:
        types = import_optional_dependency("google.generativeai.types")
        protos = import_optional_dependency("google.generativeai.protos")

        if isinstance(content, TextMessageContent):
            return content.artifact.to_text()
        elif isinstance(content, ImageMessageContent):
            return types.ContentDict(mime_type=content.artifact.mime_type, data=content.artifact.value)
        elif isinstance(content, ActionCallMessageContent):
            action = content.artifact.value

            return protos.Part(function_call=protos.FunctionCall(name=action.tag, args=action.input))
        elif isinstance(content, ActionResultMessageContent):
            artifact = content.artifact

            return protos.Part(
                function_response=protos.FunctionResponse(
                    name=content.action.to_native_tool_name(),
                    response=artifact.to_dict(),
                ),
            )
        elif isinstance(content, GenericMessageContent):
            return content.artifact.value
        else:
            raise ValueError(f"Unsupported prompt stack content type: {type(content)}")

    def __to_prompt_stack_message_content(self, content: Part) -> BaseMessageContent:
        if content.text:
            return TextMessageContent(TextArtifact(content.text))
        elif content.function_call:
            function_call = content.function_call

            name, path = ToolAction.from_native_tool_name(function_call.name)

            args = dict(function_call.args.items())
            return ActionCallMessageContent(
                artifact=ActionArtifact(value=ToolAction(tag=function_call.name, name=name, path=path, input=args)),
            )
        else:
            raise ValueError(f"Unsupported message content type {content}")

    def __to_prompt_stack_delta_message_content(self, content: Part) -> BaseDeltaMessageContent:
        if content.text:
            return TextDeltaMessageContent(content.text)
        elif content.function_call:
            function_call = content.function_call

            name, path = ToolAction.from_native_tool_name(function_call.name)

            args = dict(function_call.args.items())
            return ActionCallDeltaMessageContent(
                tag=function_call.name,
                name=name,
                path=path,
                partial_input=json.dumps(args),
            )
        else:
            raise ValueError(f"Unsupported message content type {content}")
