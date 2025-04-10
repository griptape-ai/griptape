from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Optional

from attrs import Factory, define, field
from pydantic import BaseModel

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
from griptape.configs import Defaults
from griptape.drivers.prompt import BasePromptDriver
from griptape.tokenizers import BaseTokenizer, GoogleTokenizer
from griptape.utils import import_optional_dependency, remove_key_in_dict_recursively
from griptape.utils.decorators import lazy_property

if TYPE_CHECKING:
    from collections.abc import Iterator

    from google.genai import Client
    from google.genai.types import Content, ContentDict, GenerateContentResponse, Part, Tool

    from griptape.drivers.prompt.base_prompt_driver import StructuredOutputStrategy
    from griptape.tools import BaseTool

logger = logging.getLogger(Defaults.logging_config.logger_name)


@define
class GooglePromptDriver(BasePromptDriver):
    """Google Prompt Driver.

    Attributes:
        api_key: Google API key.
        model: Google model name.
        client: Custom `GenerativeModel` client.
        top_p: Optional value for top_p.
        top_k: Optional value for top_k.
    """

    api_key: Optional[str] = field(default=None, kw_only=True, metadata={"serializable": False})
    model: str = field(kw_only=True, metadata={"serializable": True})
    tokenizer: BaseTokenizer = field(
        default=Factory(lambda self: GoogleTokenizer(api_key=self.api_key, model=self.model), takes_self=True),
        kw_only=True,
    )
    top_p: Optional[float] = field(default=None, kw_only=True, metadata={"serializable": True})
    top_k: Optional[int] = field(default=None, kw_only=True, metadata={"serializable": True})
    use_native_tools: bool = field(default=True, kw_only=True, metadata={"serializable": True})
    structured_output_strategy: StructuredOutputStrategy = field(
        default="native", kw_only=True, metadata={"serializable": True}
    )
    tool_choice: str = field(default="auto", kw_only=True, metadata={"serializable": True})

    _client: Client = field(default=None, kw_only=True, alias="client", metadata={"serializable": False})

    @lazy_property()
    def client(self) -> Client:
        genai = import_optional_dependency("google.genai")
        return genai.Client(api_key=self.api_key)

    @observable
    def try_run(self, prompt_stack: PromptStack) -> Message:
        params = self._base_params(prompt_stack)
        logging.debug(params)
        response = self.client.models.generate_content(**params)
        logging.debug(response.model_dump())

        usage_metadata = response.usage_metadata

        return Message(
            content=self.__to_prompt_stack_message_content(response),
            role=Message.ASSISTANT_ROLE,
            usage=Message.Usage(
                input_tokens=usage_metadata.prompt_token_count if usage_metadata else None,
                output_tokens=usage_metadata.candidates_token_count if usage_metadata else None,
            ),
        )

    @observable
    def try_stream(self, prompt_stack: PromptStack) -> Iterator[DeltaMessage]:
        params = self._base_params(prompt_stack)
        logging.debug(params)
        response = self.client.models.generate_content_stream(**params)

        prompt_token_count = None
        for chunk in response:
            logger.debug(chunk.model_dump())
            usage_metadata = chunk.usage_metadata

            content = self.__to_prompt_stack_delta_message_content(chunk)
            # Only want to output the prompt token count once since it is static each chunk
            if prompt_token_count is None:
                yield DeltaMessage(
                    content=content,
                    usage=DeltaMessage.Usage(
                        input_tokens=usage_metadata.prompt_token_count if usage_metadata else None,
                        output_tokens=usage_metadata.candidates_token_count if usage_metadata else None,
                    ),
                )
            else:
                yield DeltaMessage(
                    content=content,
                    usage=DeltaMessage.Usage(
                        output_tokens=usage_metadata.candidates_token_count if usage_metadata else None
                    ),
                )

    def _base_params(self, prompt_stack: PromptStack) -> dict:
        types = import_optional_dependency("google.genai.types")

        system_messages = prompt_stack.system_messages
        system_instruction = None
        if system_messages:
            system_instruction = "".join([system_message.to_text() for system_message in system_messages])

        params = {
            "model": self.model,
            "contents": self.__to_google_messages(prompt_stack),
        }

        config = {
            "stop_sequences": [] if self.use_native_tools else self.tokenizer.stop_sequences,
            "max_output_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "system_instruction": system_instruction,
            "automatic_function_calling": types.AutomaticFunctionCallingConfig(disable=True),
            **self.extra_params,
        }

        if (
            self.structured_output_strategy == "native"
            and isinstance(prompt_stack.output_schema, type)
            and issubclass(prompt_stack.output_schema, BaseModel)
        ):
            config["response_schema"] = prompt_stack.output_schema

        if prompt_stack.tools and self.use_native_tools:
            config["tool_config"] = {"function_calling_config": {"mode": self.tool_choice}}

            if prompt_stack.output_schema is not None and self.structured_output_strategy == "tool":
                config["tool_config"]["function_calling_config"]["mode"] = "auto"

            config["tools"] = self.__to_google_tools(prompt_stack.tools)

        params["config"] = types.GenerateContentConfig(**config)

        return params

    def __to_google_messages(self, prompt_stack: PromptStack) -> list[Content]:
        types = import_optional_dependency("google.genai.types")

        return [
            types.Content(
                role=self.__to_google_role(message),
                parts=[self.__to_google_message_content(content) for content in message.content],
            )
            for message in prompt_stack.messages
            if not message.is_system()
        ]

    def __to_google_role(self, message: Message) -> str:
        if message.is_assistant():
            return "model"
        return "user"

    def __to_google_tools(self, tools: list[BaseTool]) -> list[Tool]:
        types = import_optional_dependency("google.genai.types")

        tool_declarations = []
        for tool in tools:
            for activity in tool.activities():
                schema = tool.to_activity_json_schema(activity, "Parameters Schema")

                if "values" in schema["properties"]:
                    schema = schema["properties"]["values"]

                schema = remove_key_in_dict_recursively(schema, "additionalProperties")
                function_declaration = types.FunctionDeclaration(
                    name=tool.to_native_tool_name(activity),
                    description=tool.activity_description(activity),
                    **(
                        {
                            "parameters": {
                                "type": schema["type"],
                                "properties": schema["properties"],
                                "required": schema.get("required", []),
                            }
                        }
                        if schema.get("properties")
                        else {}
                    ),
                )
                google_tool = types.Tool(function_declarations=[function_declaration])

                tool_declarations.append(google_tool)

        return tool_declarations

    def __to_google_message_content(self, content: BaseMessageContent) -> ContentDict | Part | str:
        types = import_optional_dependency("google.genai.types")

        if isinstance(content, TextMessageContent):
            return types.Part.from_text(text=content.artifact.to_text())
        if isinstance(content, ImageMessageContent):
            return types.Part.from_bytes(mime_type=content.artifact.mime_type, data=content.artifact.value)
        if isinstance(content, ActionCallMessageContent):
            action = content.artifact.value

            return types.Part(function_call=types.FunctionCall(name=action.tag, args=action.input))
        if isinstance(content, ActionResultMessageContent):
            artifact = content.artifact

            return types.Part(
                function_response=types.FunctionResponse(
                    name=content.action.to_native_tool_name(),
                    response=artifact.to_dict(),
                ),
            )
        if isinstance(content, GenericMessageContent):
            file = content.artifact.value
            return types.Part.from_uri(file_uri=file.uri, mime_type=file.mime_type)
        raise ValueError(f"Unsupported prompt stack content type: {type(content)}")

    def __to_prompt_stack_message_content(self, content: GenerateContentResponse) -> list[BaseMessageContent]:
        if content.text:
            return [TextMessageContent(TextArtifact(content.text))]
        if content.function_calls:
            return [
                ActionCallMessageContent(
                    ActionArtifact(
                        ToolAction(
                            tag=function_call.name,
                            name=ToolAction.from_native_tool_name(function_call.name)[0],
                            path=ToolAction.from_native_tool_name(function_call.name)[1],
                            input=function_call.args or {},
                        ),
                    ),
                )
                for function_call in content.function_calls
                if function_call.name
            ]

        return []

    def __to_prompt_stack_delta_message_content(self, content: GenerateContentResponse) -> BaseDeltaMessageContent:
        if content.text:
            return TextDeltaMessageContent(content.text)
        if content.function_calls:
            function_call = content.function_calls[0]

            args = function_call.args
            return ActionCallDeltaMessageContent(
                tag=function_call.name,
                name=ToolAction.from_native_tool_name(function_call.name)[0] if function_call.name else None,
                path=ToolAction.from_native_tool_name(function_call.name)[1] if function_call.name else None,
                partial_input=json.dumps(args) if args else None,
            )
        raise ValueError(f"Unsupported message content type {content}")
