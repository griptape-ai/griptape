from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Optional

from attrs import Attribute, Factory, define, field

from griptape.artifacts import ActionArtifact, TextArtifact
from griptape.artifacts.image_artifact import ImageArtifact
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
from griptape.utils import (
    import_optional_dependency,
    remove_key_in_dict_recursively,
)
from griptape.utils.decorators import lazy_property

if TYPE_CHECKING:
    from collections.abc import Iterator

    from google.genai import Client
    from google.genai import types

    from griptape.drivers.prompt.base_prompt_driver import StructuredOutputStrategy
    from griptape.tools import BaseTool

logger = logging.getLogger(Defaults.logging_config.logger_name)


@define
class GooglePromptDriver(BasePromptDriver):
    """Google Prompt Driver.

    Attributes:
        api_key: Google API key.
        model: Google model name.
        client: Custom `Client` instance.
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
        default="tool", kw_only=True, metadata={"serializable": True}
    )
    tool_choice: str = field(default="auto", kw_only=True, metadata={"serializable": True})
    _client: Optional[Client] = field(default=None, kw_only=True, alias="client", metadata={"serializable": False})

    @structured_output_strategy.validator  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
    def validate_structured_output_strategy(self, _: Attribute, value: str) -> str:
        if value == "native":
            raise ValueError(f"{__class__.__name__} does not support `{value}` structured output strategy.")

        return value

    @lazy_property()
    def client(self) -> Client:
        genai = import_optional_dependency("google.genai")

        return genai.Client(api_key=self.api_key)

    @observable
    def try_run(self, prompt_stack: PromptStack) -> Message:
        contents = self.__to_google_messages(prompt_stack)
        config = self._build_config(prompt_stack)
        logger.debug((contents, config))

        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config=config,
        )
        logger.debug(response)

        # Access the first candidate
        if not response.candidates or not response.candidates[0].content:
            raise ValueError("No response content received from Google API")

        candidate = response.candidates[0]
        content = candidate.content

        if not content or not content.parts:
            raise ValueError("No content parts in response from Google API")

        return Message(
            content=[self.__to_prompt_stack_message_content(part) for part in content.parts],
            role=Message.ASSISTANT_ROLE,
            usage=Message.Usage(
                input_tokens=candidate.token_count or 0,
                output_tokens=candidate.token_count or 0,
            ),
        )

    @observable
    def try_stream(self, prompt_stack: PromptStack) -> Iterator[DeltaMessage]:
        contents = self.__to_google_messages(prompt_stack)
        config = self._build_config(prompt_stack)
        logger.debug((contents, config))

        response = self.client.models.generate_content_stream(
            model=self.model,
            contents=contents,
            config=config,
        )

        prompt_token_count = None
        for chunk in response:
            logger.debug(chunk)
            candidate = chunk.candidates[0] if chunk.candidates else None
            if not candidate or not candidate.content:
                continue

            content_part = candidate.content.parts[0] if candidate.content.parts else None
            delta_content = self.__to_prompt_stack_delta_message_content(content_part) if content_part else None

            # Only want to output the prompt token count once since it is static each chunk
            if prompt_token_count is None:
                prompt_token_count = candidate.token_count or 0
                yield DeltaMessage(
                    content=delta_content,
                    usage=DeltaMessage.Usage(
                        input_tokens=prompt_token_count,
                        output_tokens=0,
                    ),
                )
            else:
                yield DeltaMessage(
                    content=delta_content,
                    usage=DeltaMessage.Usage(output_tokens=candidate.token_count or 0),
                )

    def _build_config(self, prompt_stack: PromptStack) -> types.GenerateContentConfig:
        types = import_optional_dependency("google.genai.types")

        # Build configuration parameters
        config_params = {
            # For some reason, providing stop sequences when streaming breaks native functions
            # https://github.com/google-gemini/generative-ai-python/issues/446
            "stop_sequences": [] if self.stream and self.use_native_tools else self.tokenizer.stop_sequences,
            "max_output_tokens": self.max_tokens,
            "temperature": self.temperature,
        }

        if self.top_p is not None:
            config_params["top_p"] = self.top_p
        if self.top_k is not None:
            config_params["top_k"] = self.top_k

        # Add extra params
        config_params.update(self.extra_params)

        # Add system instruction
        system_messages = prompt_stack.system_messages
        if system_messages:
            system_text = "\n".join([msg.to_text() for msg in system_messages])
            config_params["system_instruction"] = system_text

        # Add tools if using native tools
        if prompt_stack.tools and self.use_native_tools:
            config_params["tools"] = self.__to_google_tools(prompt_stack.tools)

            # Set tool choice mode
            tool_mode = self.tool_choice.upper()  # New SDK uses uppercase modes
            if prompt_stack.output_schema is not None and self.structured_output_strategy == "tool":
                tool_mode = "AUTO"

            # Use typed objects for tool configuration
            config_params["tool_config"] = types.ToolConfig(
                function_calling_config=types.FunctionCallingConfig(mode=tool_mode)
            )

        return types.GenerateContentConfig(**config_params)

    def __to_google_messages(self, prompt_stack: PromptStack) -> list:
        types = import_optional_dependency("google.genai.types")

        contents = []
        for message in prompt_stack.messages:
            if message.is_system():
                continue

            parts = [self.__to_google_message_content(content) for content in message.content]
            content = types.Content(
                role=self.__to_google_role(message),
                parts=parts,
            )
            contents.append(content)

        return contents

    def __to_google_role(self, message: Message) -> str:
        if message.is_assistant():
            return "model"
        return "user"

    def __to_google_tools(self, tools: list[BaseTool]) -> list[types.Tool]:
        types = import_optional_dependency("google.genai.types")

        function_declarations = []
        for tool in tools:
            for activity in tool.activities():
                schema = tool.to_activity_json_schema(activity, "Parameters Schema")

                if "values" in schema["properties"]:
                    schema = schema["properties"]["values"]

                schema = remove_key_in_dict_recursively(schema, "additionalProperties")
                schema = remove_key_in_dict_recursively(schema, "title", preserve_under_key="properties")

                # Build parameters_json_schema if properties exist
                params_schema = None
                if schema.get("properties"):
                    params_schema = {
                        "type": schema["type"],
                        "properties": schema["properties"],
                    }
                    if schema.get("required"):
                        params_schema["required"] = schema["required"]

                function_declaration = types.FunctionDeclaration(
                    name=tool.to_native_tool_name(activity),
                    description=tool.activity_description(activity),
                    parameters_json_schema=params_schema,
                )

                function_declarations.append(function_declaration)

        # Wrap all function declarations in a single Tool object
        return [types.Tool(function_declarations=function_declarations)]

    def __to_google_message_content(self, content: BaseMessageContent) -> types.Part:
        types = import_optional_dependency("google.genai.types")

        if isinstance(content, TextMessageContent):
            return types.Part.from_text(text=content.artifact.to_text())
        if isinstance(content, ImageMessageContent):
            if isinstance(content.artifact, ImageArtifact):
                # Create inline data part for images
                return types.Part(
                    inline_data=types.Blob(
                        mime_type=content.artifact.mime_type,
                        data=content.artifact.value,
                    )
                )
            # TODO: Google requires uploading to the files endpoint: https://ai.google.dev/gemini-api/docs/image-understanding#upload-image
            # Can be worked around by using GenericMessageContent, similar to videos.
            raise ValueError(f"Unsupported image artifact type: {type(content.artifact)}")
        if isinstance(content, ActionCallMessageContent):
            action = content.artifact.value

            return types.Part.from_function_call(
                name=action.tag,
                args=action.input,
            )
        if isinstance(content, ActionResultMessageContent):
            artifact = content.artifact

            return types.Part.from_function_response(
                name=content.action.to_native_tool_name(),
                response=artifact.to_dict(),
            )
        if isinstance(content, GenericMessageContent):
            # For generic content, try to convert to text
            # TODO: This may need more sophisticated handling
            return types.Part.from_text(text=str(content.artifact.value))
        raise ValueError(f"Unsupported prompt stack content type: {type(content)}")

    def __to_prompt_stack_message_content(self, content: types.Part) -> BaseMessageContent:
        if content.text:
            return TextMessageContent(TextArtifact(content.text))
        if content.function_call:
            function_call = content.function_call

            if not function_call.name:
                raise ValueError("Function call missing name")

            name, path = ToolAction.from_native_tool_name(function_call.name)

            return ActionCallMessageContent(
                artifact=ActionArtifact(
                    value=ToolAction(tag=function_call.name, name=name, path=path, input=function_call.args or {})
                ),
            )
        raise ValueError(f"Unsupported message content type {content}")

    def __to_prompt_stack_delta_message_content(self, content: types.Part) -> BaseDeltaMessageContent:
        if content.text:
            return TextDeltaMessageContent(content.text)
        if content.function_call:
            function_call = content.function_call

            if not function_call.name:
                raise ValueError("Function call missing name")

            name, path = ToolAction.from_native_tool_name(function_call.name)

            return ActionCallDeltaMessageContent(
                tag=function_call.name,
                name=name,
                path=path,
                partial_input=json.dumps(function_call.args or {}),
            )
        raise ValueError(f"Unsupported message content type {content}")
