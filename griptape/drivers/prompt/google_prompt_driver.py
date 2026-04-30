from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, cast

from attrs import Factory, define, field

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
    from google.genai.types import (
        Content,
        ContentListUnionDict,
        GenerateContentResponse,
        Part,
    )

    from griptape.drivers.prompt.base_prompt_driver import StructuredOutputStrategy
    from griptape.tools import BaseTool

logger = logging.getLogger(Defaults.logging_config.logger_name)


@define
class GooglePromptDriver(BasePromptDriver):
    """Google Prompt Driver.

    Attributes:
        api_key: Google API key.
        model: Google model name.
        client: Custom `google.genai.Client`.
        top_p: Optional value for top_p.
        top_k: Optional value for top_k.
    """

    api_key: str | None = field(default=None, kw_only=True, metadata={"serializable": False})
    model: str = field(kw_only=True, metadata={"serializable": True})
    tokenizer: BaseTokenizer = field(
        default=Factory(lambda self: GoogleTokenizer(api_key=self.api_key, model=self.model), takes_self=True),
        kw_only=True,
    )
    top_p: float | None = field(default=None, kw_only=True, metadata={"serializable": True})
    top_k: int | None = field(default=None, kw_only=True, metadata={"serializable": True})
    use_native_tools: bool = field(default=True, kw_only=True, metadata={"serializable": True})
    structured_output_strategy: StructuredOutputStrategy = field(
        default="tool", kw_only=True, metadata={"serializable": True}
    )
    tool_choice: str = field(default="auto", kw_only=True, metadata={"serializable": True})
    _client: Client | None = field(default=None, kw_only=True, alias="client", metadata={"serializable": False})

    @lazy_property()
    def client(self) -> Client:
        genai = import_optional_dependency("google.genai")

        return genai.Client(api_key=self.api_key)

    @observable
    def try_run(self, prompt_stack: PromptStack) -> Message:
        types = import_optional_dependency("google.genai.types")

        messages = self.__to_google_messages(prompt_stack)
        params = self._base_params(prompt_stack)
        config = types.GenerateContentConfig(**params)
        logger.debug((messages, params))
        response: GenerateContentResponse = self.client.models.generate_content(
            model=self.model,
            contents=cast("ContentListUnionDict", messages),
            config=config,
        )
        logger.debug(response.model_dump())

        usage_metadata = response.usage_metadata
        parts = response.candidates[0].content.parts if response.candidates and response.candidates[0].content else []

        return Message(
            content=[
                self.__to_prompt_stack_message_content(part)
                for part in (parts or [])
                if not self.__is_thought_part(part)
            ],
            role=Message.ASSISTANT_ROLE,
            usage=Message.Usage(
                input_tokens=usage_metadata.prompt_token_count if usage_metadata else None,
                output_tokens=usage_metadata.candidates_token_count if usage_metadata else None,
            ),
        )

    @observable
    def try_stream(self, prompt_stack: PromptStack) -> Iterator[DeltaMessage]:
        types = import_optional_dependency("google.genai.types")

        messages = self.__to_google_messages(prompt_stack)
        params = self._base_params(prompt_stack)
        config = types.GenerateContentConfig(**params)
        logger.debug((messages, params))
        response = self.client.models.generate_content_stream(
            model=self.model,
            contents=cast("ContentListUnionDict", messages),
            config=config,
        )

        prompt_token_count = None
        for chunk in response:
            logger.debug(chunk.model_dump())
            usage_metadata = chunk.usage_metadata

            parts = chunk.candidates[0].content.parts if chunk.candidates and chunk.candidates[0].content else None
            # Gemini thinking models emit reasoning-only chunks (e.g. a bare `thought_signature`)
            # with no text or function_call; skip them since Griptape has no thought content type.
            non_thought_part = (
                next((part for part in parts if not self.__is_thought_part(part)), None) if parts else None
            )
            content = self.__to_prompt_stack_delta_message_content(non_thought_part) if non_thought_part else None

            # Only want to output the prompt token count once since it is static each chunk
            if prompt_token_count is None and usage_metadata is not None:
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
                    usage=DeltaMessage.Usage(
                        output_tokens=usage_metadata.candidates_token_count if usage_metadata else None,
                    ),
                )

    def _base_params(self, prompt_stack: PromptStack) -> dict:
        types = import_optional_dependency("google.genai.types")

        system_messages = prompt_stack.system_messages
        system_instruction = None
        if system_messages:
            system_instruction = types.Content(
                role="system",
                parts=[types.Part.from_text(text=system_message.to_text()) for system_message in system_messages],
            )

        params = {
            # For some reason, providing stop sequences when streaming breaks native functions
            # https://github.com/google-gemini/generative-ai-python/issues/446
            "stop_sequences": [] if self.stream and self.use_native_tools else self.tokenizer.stop_sequences,
            "max_output_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "top_k": self.top_k,
            **({"system_instruction": system_instruction} if system_instruction is not None else {}),
            **self.extra_params,
        }

        if prompt_stack.tools and self.use_native_tools:
            mode = self.tool_choice.upper()

            if prompt_stack.output_schema is not None and self.structured_output_strategy == "tool":
                mode = "AUTO"

            params["tool_config"] = types.ToolConfig(
                function_calling_config=types.FunctionCallingConfig(mode=mode),
            )
            params["tools"] = self.__to_google_tools(prompt_stack.tools)

        if prompt_stack.output_schema is not None and self.structured_output_strategy == "native":
            params["response_mime_type"] = "application/json"
            params["response_json_schema"] = prompt_stack.to_output_json_schema()

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

    def __to_google_tools(self, tools: list[BaseTool]) -> list:
        types = import_optional_dependency("google.genai.types")

        function_declarations = []
        for tool in tools:
            for activity in tool.activities():
                schema = tool.to_activity_json_schema(activity, "Parameters Schema")

                if "values" in schema["properties"]:
                    schema = schema["properties"]["values"]

                schema = remove_key_in_dict_recursively(schema, "additionalProperties")
                schema = remove_key_in_dict_recursively(schema, "title", preserve_under_key="properties")
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

                function_declarations.append(function_declaration)

        return [types.Tool(function_declarations=function_declarations)]

    def __to_google_message_content(self, content: BaseMessageContent) -> Part:
        types = import_optional_dependency("google.genai.types")

        if isinstance(content, TextMessageContent):
            return types.Part.from_text(text=content.artifact.to_text())
        if isinstance(content, ImageMessageContent):
            if isinstance(content.artifact, ImageArtifact):
                return types.Part.from_bytes(data=content.artifact.value, mime_type=content.artifact.mime_type)
            # TODO: Google requires uploading to the files endpoint: https://ai.google.dev/gemini-api/docs/image-understanding#upload-image
            # Can be worked around by using GenericMessageContent, similar to videos.
            raise ValueError(f"Unsupported image artifact type: {type(content.artifact)}")
        if isinstance(content, ActionCallMessageContent):
            action = content.artifact.value

            return types.Part.from_function_call(name=action.tag, args=action.input)
        if isinstance(content, ActionResultMessageContent):
            artifact = content.artifact

            return types.Part.from_function_response(
                name=content.action.to_native_tool_name(),
                response=artifact.to_dict(),
            )
        if isinstance(content, GenericMessageContent):
            value = content.artifact.value
            if isinstance(value, str):
                return types.Part.from_text(text=value)
            return value
        raise ValueError(f"Unsupported prompt stack content type: {type(content)}")

    def __is_thought_part(self, content: Part) -> bool:
        # Gemini thinking models emit reasoning-only parts (e.g. a bare `thought_signature`)
        # with no text or function_call; Griptape has no thought content type, so callers skip them.
        return bool((content.thought or content.thought_signature) and not content.text and not content.function_call)

    def __to_prompt_stack_message_content(self, content: Part) -> BaseMessageContent:
        if content.text:
            return TextMessageContent(TextArtifact(content.text))
        if content.function_call:
            function_call = content.function_call
            tag = function_call.name or ""

            name, path = ToolAction.from_native_tool_name(tag)

            args = function_call.args or {}
            return ActionCallMessageContent(
                artifact=ActionArtifact(value=ToolAction(tag=tag, name=name, path=path, input=args)),
            )
        raise ValueError(f"Unsupported message content type {content}")

    def __to_prompt_stack_delta_message_content(self, content: Part) -> BaseDeltaMessageContent:
        if content.text:
            return TextDeltaMessageContent(content.text)
        if content.function_call:
            function_call = content.function_call
            tag = function_call.name or ""

            name, path = ToolAction.from_native_tool_name(tag)

            args = function_call.args or {}
            return ActionCallDeltaMessageContent(
                tag=tag,
                name=name,
                path=path,
                partial_input=json.dumps(args),
            )
        raise ValueError(f"Unsupported message content type {content}")
