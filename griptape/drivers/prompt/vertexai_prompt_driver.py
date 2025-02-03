# need google application credentials environment variable
# https://cloud.google.com/vertex-ai/docs/start/client-libraries
# https://cloud.google.com/python/docs/reference/aiplatform/latest
# https://cloud.google.com/python/docs/reference/aiplatform/latest?hl=en
# https://cloud.google.com/vertex-ai/generative-ai/docs/reference/python/latest/vertexai.preview.generative_models.GenerativeModel


# Google gemini doesn't work with the old version of parts and whatnot - needs it's own implementation
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from attrs import Attribute, Factory, define, field
from schema import Schema
from griptape.drivers import prompt
from vertexai.generative_models import Part

from griptape.common import (
    BaseDeltaMessageContent,
    DeltaMessage,
    Message,
    PromptStack,
    TextDeltaMessageContent,
    TextMessageContent,
    observable,
)
from griptape.common.prompt_stack.contents.generic_message_content import (
    GenericMessageContent,
)
from griptape.common.prompt_stack.contents.image_message_content import (
    ImageMessageContent,
)
from griptape.artifacts import GenericArtifact
from griptape.configs import Defaults
from griptape.drivers.prompt.base_prompt_driver import BasePromptDriver
from griptape.structures.workflow import Workflow
from griptape.tasks.prompt_task import PromptTask
from griptape.tokenizers.vertexai_google_tokenizer import VertexAIGoogleTokenizer
from griptape.tools.base_tool import BaseTool
from griptape.utils.decorators import lazy_property
from griptape.utils.dict_utils import remove_key_in_dict_recursively
from griptape.utils.import_utils import import_optional_dependency

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

    from google.auth.credentials import Credentials
    from vertexai.generative_models import Content, GenerationResponse, GenerativeModel

    from griptape.common.prompt_stack.contents.base_message_content import (
        BaseMessageContent,
    )
    from griptape.drivers.prompt.base_prompt_driver import StructuredOutputStrategy
    from griptape.tokenizers.base_tokenizer import BaseTokenizer
from rich.pretty import pprint  # will automatically nicely format things

import os
import json
from google.oauth2 import service_account

# need to install - pip install --upgrade google-cloud-aiplatform How do i do this?
logger = logging.getLogger(Defaults.logging_config.logger_name)


@define
class VertexAIGooglePromptDriver(BasePromptDriver):
    """Vertex AI Google Prompt Driver.

    Attributes:
        project: str
        location: str
        experiment: str
        staging_bucket: str
        credentials: google.auth.credentials.Credentials
        encryption_spec_key_name: str
        service_account: str
        model: str
        top_p: Optional value for top_p
        top_k: Optional value for top_k
        client: Custom `GenerativeModel` client.
    """

    # These are all the fields for the VertexAI SDK
    project: str = field(kw_only=True, metadata={"serializable": True})
    location: str = field(kw_only=True, metadata={"serializable": True})
    response_schema: Optional[dict] = field(
        default=None, kw_only=True, metadata={"serializable": True}
    )
    response_mime_type: Optional[str] = field(
        default="application/json", kw_only=True, metadata={"serializable": True}
    )
    credentials: Credentials = field(
        kw_only=True, metadata={"serializable": False}
    )  # non private field

    # Necessary for Google Prompt Driver as well
    top_p: Optional[float] = field(
        default=None, kw_only=True, metadata={"serializable": True}
    )
    top_k: Optional[int] = field(
        default=None, kw_only=True, metadata={"serializable": True}
    )
    use_native_tools: bool = field(
        default=True, kw_only=True, metadata={"serializable": True}
    )
    tokenizer: BaseTokenizer = field(
        # keep this simple for now!
        default=Factory(
            lambda self: VertexAIGoogleTokenizer(
                model=self.model,
                project=self.project,
                location=self.location,
                credentials=self.credentials,
            ),
            takes_self=True,
        ),
        kw_only=True,
    )
    structured_output_strategy: StructuredOutputStrategy = field(
        default="tool", kw_only=True, metadata={"serializable": True}
    )
    tool_choice: str = field(
        default="auto", kw_only=True, metadata={"serializable": True}
    )
    _client: GenerativeModel = field(
        default=None, kw_only=True, alias="client", metadata={"serializable": False}
    )

    # Fields that might not be necessary
    encryption_spec_key_name: Optional[str] = field(
        default=None, kw_only=True, metadata={"serializable": False}
    )
    service_account: Optional[str] = field(
        default=None, kw_only=True, metadata={"serializable": False}
    )
    experiment: Optional[str] = field(
        default=None, kw_only=True, metadata={"serializable": True}
    )
    staging_bucket: Optional[str] = field(
        default=None, kw_only=True, metadata={"serializable": True}
    )

    @structured_output_strategy.validator
    def validate_structured_output_strategy(self, _: Attribute, value: str) -> str:
        if value == "native":
            raise ValueError(
                f"{__class__.__name__} does not support `{value}` structured output strategy."
            )

        return value

    # Initialize VertexAI with proper credentials & values
    @lazy_property()
    def client(self) -> GenerativeModel:
        vertexai = import_optional_dependency("vertexai")
        vertexai.init(
            project=self.project,
            location=self.location,
            experiment=self.experiment,
            staging_bucket=self.staging_bucket,
            credentials=self.credentials,
            encryption_spec_key_name=self.encryption_spec_key_name,
            service_account=self.service_account,
        )
        return vertexai.generative_models.GenerativeModel(model_name=self.model)

    @observable
    def try_run(self, prompt_stack: PromptStack) -> Message:
        vertexai = import_optional_dependency("vertexai.generative_models")

        messages = self.__to_google_messages(prompt_stack)
        params = self._base_params(prompt_stack)
        system_messages = vertexai.Content(
            role="user",
            parts=[
                vertexai.Part.from_text(text=system_message.to_text())
                for system_message in prompt_stack.system_messages
            ],
        )
        messages.append(system_messages)
        response: GenerationResponse = self.client.generate_content(messages, **params)
        usage_metadata = response.usage_metadata
        # TODO: modify for function calls
        return Message(
            content=response.text,  # TODO: Modify for try_stream potentially.
            role=Message.ASSISTANT_ROLE,
            usage=Message.Usage(
                input_tokens=usage_metadata.prompt_token_count,
                output_tokens=usage_metadata.candidates_token_count,
            ),
        )

    # Streaming is not currently supported with VertexAI? Says there is no stream parameter - can't remember if that's in GenerationResponse or somewhere else.
    # Does have streaming apparently - iterator so i can check each chunk if it's text/function/etc
    @observable
    def try_stream(self, prompt_stack: PromptStack) -> Iterator[DeltaMessage]:
        messages = self.__to_google_messages(prompt_stack)
        params = {
            **self._base_params(prompt_stack),
            "stream": True,
        }  # TODO: Check if other params must be modified (generation_config?)
        response: Iterable[GenerationResponse] = self.client.generate_content(
            messages, **params
        )
        prompt_token_count = None
        for chunk in response:
            usage_metadata = chunk.usage_metadata
            content = (
                self.__to_prompt_stack_delta_message_content(
                    chunk.candidates[0].content.parts[0]
                )
                if chunk.candidates[0].content.parts
                else None
            )
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
                    usage=DeltaMessage.Usage(
                        output_tokens=usage_metadata.candidates_token_count
                    ),
                )

    def _base_params(self, prompt_stack: PromptStack) -> dict:
        vertexai = import_optional_dependency("vertexai.generative_models")
        system_messages = prompt_stack.system_messages
        if system_messages:
            # Fix this it is kind of hacky - system instruction. Want to set system rules at the time we run, not before.
            self.client._system_instruction = vertexai.Content(
                role="system",
                parts=[
                    vertexai.Part.from_text(text=system_message.to_text())
                    for system_message in system_messages
                ],
            )
            logger.debug(self.client._system_instruction)
        params = {
            "generation_config": vertexai.GenerationConfig(
                temperature=self.temperature,
                top_k=self.top_k,
                top_p=self.top_p,
                max_output_tokens=self.max_tokens,
                response_schema=self.response_schema,
                response_mime_type=self.response_mime_type,
                **self.extra_params,
            )
        }
        if prompt_stack.tools and self.use_native_tools:
            params["tool_config"] = {
                "function_calling_config": {"mode": self.tool_choice}
            }
            params["tools"] = self.__to_google_tools(prompt_stack.tools)
        return params

    # TODO: Implement later if necessary for Driver to be added to the framework
    def __to_google_tools(self, tools: list[BaseTool]) -> list[dict]:
        tool_declarations = []
        for tool in tools:
            for activity in tool.activities():
                schema = (tool.activity_schema(activity) or Schema({})).json_schema(
                    "Parameters Schema"
                )
                if "values" in schema["properties"]:
                    schema = schema["properties"]["values"]
                schema = remove_key_in_dict_recursively(schema, "additionalProperties")
                tool_declaration = "f"  # TODO figure out vertex ai driver
                tool_declarations.append(tool_declaration)
        return tool_declarations

    def __to_google_messages(self, prompt_stack: PromptStack) -> list[Content]:
        content = import_optional_dependency("vertexai.generative_models")
        return [
            content.Content(
                role=self.__to_google_role(message),
                parts=[
                    self.__to_google_message_content(content)
                    for content in message.content
                ],
            )
            for message in prompt_stack.messages
            if not message.is_system()
        ]

    def __to_google_role(self, message: Message) -> str:
        if message.is_assistant():
            return "model"
        else:
            return "user"

    def __to_google_message_content(
        self, content: BaseMessageContent
    ) -> Content | Part | str:
        if isinstance(content, TextMessageContent):
            return Part.from_text(content.artifact.to_text())
        elif isinstance(content, ImageMessageContent):
            return Part.from_data(
                mime_type=content.artifact.mime_type, data=content.artifact.value
            )
        elif isinstance(content, GenericMessageContent):
            # Just returns content.artifact.value, it's on the user to pass a Part object to the driver.
            return content.artifact.value
        else:
            raise ValueError(f"Unsupported prompt stack content type: {type(content)}")

    def __to_prompt_stack_delta_message_content(
        self, content: Part
    ) -> BaseDeltaMessageContent:
        json_format = import_optional_dependency("google.protobuf.json_format")

        if content.text:
            return TextDeltaMessageContent(content.text)
        # TODO: Implement later when necessary.
        # elif content.function_call:
        #     function_call = content.function_call

        #     name, path = ToolAction.from_native_tool_name(function_call.name)

        #     args = json_format.MessageToDict(function_call._pb).get("args", {})
        #     return ActionCallDeltaMessageContent(
        #         tag=function_call.name,
        #         name=name,
        #         path=path,
        #         partial_input=json.dumps(args),
        #     )
        else:
            raise ValueError(f"Unsupported message content type {content}")


def _get_response_schema():
    return {
        "type": "object",
        "properties": {
            "criteria_found": {"type": "boolean"},
            "description": {"type": "string"},
            "time_stamp": {"type": "integer"},
        },
        "required": ["criteria_found", "description"],
    }


# if __name__ == "__main__":
# uri = "gs://gt-airloom-video-analysis/front_entry-1737417990-1737418020.mp4"
# creds = os.environ["GOOGLE_CREDENTIALS"]
# key_data = json.loads(creds)
# credentials = service_account.Credentials.from_service_account_info(key_data)
# schema = _get_response_schema()

# # Initialize the driver here
# driver = VertexAIGooglePromptDriver(
#     project="griptape-cloud-dev",
#     location="us-west1",
#     credentials=credentials,
#     response_schema=schema,
#     model="gemini-1.5-flash-002",
# )
# video_part = Part.from_uri(uri, mime_type="video/mp4")
# stack = PromptStack()
# import griptape
# from griptape.artifacts import GenericArtifact

# stack.add_message(GenericArtifact(video_part), role="USER")
# stack.add_message("Is there a person in this video?", role="USER")
# # result = driver.try_run(stack)
# workflow = Workflow(
#     # rules=[
#     #     Rule(
#     #         "You are skilled at determining different scenarios in a high end restaurant"
#     #     ),
#     #     Rule("Be as descriptive as possible"),
#     # ]
# )
# video_part = Part.from_uri(uri, mime_type="video/mp4")
# query = "Is there a person in this video?"
# prompt_task = PromptTask(input=[uri, query], prompt_driver=driver)
# print("Prompt task prompt stack: ", prompt_task.prompt_stack)
# print("Normal prompt stack: ", stack.messages)
# workflow.add_task(prompt_task)
# result = workflow.run()
# print(result.output)
