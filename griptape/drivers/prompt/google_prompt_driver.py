from __future__ import annotations

from collections.abc import Iterator
import json
from typing import TYPE_CHECKING, Any, Optional

from attrs import Factory, define, field

from griptape.common import (
    BasePromptStackContent,
    DeltaPromptStackMessage,
    TextDeltaPromptStackContent,
    ImagePromptStackContent,
    PromptStack,
    PromptStackMessage,
    TextPromptStackContent,
    ActionCallPromptStackContent,
    ActionResultPromptStackContent,
    DeltaActionCallPromptStackContent,
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
    model_client: Any = field(default=Factory(lambda self: self._default_model_client(), takes_self=True), kw_only=True)
    tokenizer: BaseTokenizer = field(
        default=Factory(lambda self: GoogleTokenizer(api_key=self.api_key, model=self.model), takes_self=True),
        kw_only=True,
    )
    top_p: Optional[float] = field(default=None, kw_only=True, metadata={"serializable": True})
    top_k: Optional[int] = field(default=None, kw_only=True, metadata={"serializable": True})
    use_native_tools: bool = field(default=True, kw_only=True, metadata={"serializable": True})
    tool_choice: str = field(default="auto", kw_only=True, metadata={"serializable": True})

    def try_run(self, prompt_stack: PromptStack) -> PromptStackMessage:
        messages = self._prompt_stack_to_messages(prompt_stack)
        response: GenerateContentResponse = self.model_client.generate_content(
            messages, **self._base_params(prompt_stack)
        )

        usage_metadata = response.usage_metadata

        return PromptStackMessage(
            content=[self.__message_content_to_prompt_stack_content(part) for part in response.parts],
            role=PromptStackMessage.ASSISTANT_ROLE,
            usage=PromptStackMessage.Usage(
                input_tokens=usage_metadata.prompt_token_count, output_tokens=usage_metadata.candidates_token_count
            ),
        )

    def try_stream(self, prompt_stack: PromptStack) -> Iterator[DeltaPromptStackMessage | BaseDeltaPromptStackContent]:
        messages = self._prompt_stack_to_messages(prompt_stack)
        response: Iterator[GenerateContentResponse] = self.model_client.generate_content(
            messages, **self._base_params(prompt_stack), stream=True
        )

        prompt_token_count = None
        for chunk in response:
            usage_metadata = chunk.usage_metadata

            for part in chunk.parts:
                yield self.__message_content_delta_to_prompt_stack_content_delta(part)

            # Only want to output the prompt token count once since it is static each chunk
            if prompt_token_count is None:
                prompt_token_count = usage_metadata.prompt_token_count
                yield DeltaPromptStackMessage(
                    content=TextDeltaPromptStackContent(chunk.text),
                    role=PromptStackMessage.ASSISTANT_ROLE,
                    usage=DeltaPromptStackMessage.Usage(
                        input_tokens=usage_metadata.prompt_token_count,
                        output_tokens=usage_metadata.candidates_token_count,
                    ),
                )
            else:
                yield DeltaPromptStackMessage(
                    content=TextDeltaPromptStackContent(chunk.text),
                    role=PromptStackMessage.ASSISTANT_ROLE,
                    usage=DeltaPromptStackMessage.Usage(output_tokens=usage_metadata.candidates_token_count),
                )

    def _base_params(self, prompt_stack: PromptStack) -> dict:
        GenerationConfig = import_optional_dependency("google.generativeai.types").GenerationConfig

        return {
            "generation_config": GenerationConfig(
                max_output_tokens=self.max_tokens, temperature=self.temperature, top_p=self.top_p, top_k=self.top_k
            ),
            **self._prompt_stack_to_tools(prompt_stack),
        }

    def _default_model_client(self) -> GenerativeModel:
        genai = import_optional_dependency("google.generativeai")
        genai.configure(api_key=self.api_key)

        return genai.GenerativeModel(self.model)

    def _prompt_stack_to_messages(self, prompt_stack: PromptStack) -> list[dict]:
        inputs = [
            {"role": self.__to_role(message), "parts": self.__to_content(message)}
            for message in prompt_stack.messages
            if not message.is_system()
        ]

        # Gemini does not have the notion of a system message, so we insert it as part of the first message in the history.
        system = next((i for i in prompt_stack.messages if i.is_system()), None)
        if system is not None:
            inputs[0]["parts"].insert(0, "\n".join(content.to_text() for content in system.content))

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

    def __message_content_to_prompt_stack_content(self, content: Part) -> BasePromptStackContent:
        MessageToDict = import_optional_dependency("google.protobuf.json_format").MessageToDict
        # https://stackoverflow.com/questions/64403737/attribute-error-descriptor-while-trying-to-convert-google-vision-response-to-dic
        content_dict = MessageToDict(content._pb)

        if "text" in content_dict:
            return TextPromptStackContent(TextArtifact(content_dict["text"]))
        elif "functionCall" in content_dict:
            function_call = content_dict["functionCall"]

            name, path = function_call["name"].split("_", 1)

            return ActionCallPromptStackContent(
                artifact=ActionArtifact(
                    value=ActionArtifact.Action(
                        tag=function_call["name"], name=name, path=path, input=function_call["args"]
                    )
                )
            )
        else:
            raise ValueError(f"Unsupported message content type {content_dict}")

    def __prompt_stack_content_message_content(self, content: BasePromptStackContent) -> ContentDict | Part | str:
        ContentDict = import_optional_dependency("google.generativeai.types").ContentDict
        Part = import_optional_dependency("google.generativeai.protos").Part
        FunctionCall = import_optional_dependency("google.generativeai.protos").FunctionCall
        FunctionResponse = import_optional_dependency("google.generativeai.protos").FunctionResponse

        if isinstance(content, TextPromptStackContent):
            return content.artifact.to_text()
        elif isinstance(content, ImagePromptStackContent):
            return ContentDict(mime_type=content.artifact.mime_type, data=content.artifact.value)
        elif isinstance(content, ActionCallPromptStackContent):
            action = content.artifact.value

            return Part(function_call=FunctionCall(name=action.tag, args=action.input))
        elif isinstance(content, ActionResultPromptStackContent):
            artifact = content.artifact

            return Part(
                function_response=FunctionResponse(
                    name=f"{content.action.name}_{content.action.path}", response=artifact.to_dict()
                )
            )

        else:
            raise ValueError(f"Unsupported prompt stack content type: {type(content)}")

    def __message_content_delta_to_prompt_stack_content_delta(self, content: Part) -> BaseDeltaPromptStackContent:
        MessageToDict = import_optional_dependency("google.protobuf.json_format").MessageToDict
        # https://stackoverflow.com/questions/64403737/attribute-error-descriptor-while-trying-to-convert-google-vision-response-to-dic
        content_dict = MessageToDict(content._pb)
        if "text" in content_dict:
            return DeltaTextPromptStackContent(content_dict["text"])
        elif "functionCall" in content_dict:
            function_call = content_dict["functionCall"]

            name, path = function_call["name"].split("_", 1)

            return DeltaActionCallPromptStackContent(
                tag=function_call["name"], name=name, path=path, delta_input=json.dumps(function_call["args"])
            )
        else:
            raise ValueError(f"Unsupported message content type {content_dict}")

    def __to_role(self, message: PromptStackMessage) -> str:
        if message.is_assistant():
            return "model"
        else:
            return "user"

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

    def __to_content(self, message: PromptStackMessage) -> list[ContentDict | str | Part]:
        return [self.__prompt_stack_content_message_content(content) for content in message.content]
