# need google application credentials environment variable
# https://cloud.google.com/vertex-ai/docs/start/client-libraries
# https://cloud.google.com/python/docs/reference/aiplatform/latest
# https://cloud.google.com/python/docs/reference/aiplatform/latest?hl=en
# https://cloud.google.com/vertex-ai/generative-ai/docs/reference/python/latest/vertexai.preview.generative_models.GenerativeModel


# Google gemini doesn't work with the old version of parts and whatnot - needs it's own implementation
from __future__ import annotations

import json
import logging
import os
from typing import TYPE_CHECKING, Optional

from attrs import Attribute, Factory, define, field
from vertexai.generative_models import Part
import vertexai.generative_models

from griptape.artifacts import TextArtifact
from griptape.artifacts.base_artifact import BaseArtifact
from griptape.artifacts.generic_artifact import GenericArtifact
from griptape.common import Message, PromptStack, TextMessageContent, observable
from griptape.common.prompt_stack.contents.generic_message_content import (
    GenericMessageContent,
)
from griptape.common.prompt_stack.contents.image_message_content import (
    ImageMessageContent,
)
from griptape.configs import Defaults
from griptape.drivers.prompt.base_prompt_driver import BasePromptDriver
from griptape.tokenizers.vertexai_google_tokenizer import VertexAIGoogleTokenizer
from griptape.utils.decorators import lazy_property
from griptape.utils.import_utils import import_optional_dependency

if TYPE_CHECKING:
    from google.auth.credentials import Credentials
    from vertexai.generative_models import Content, GenerationResponse, GenerativeModel

    from griptape.common.prompt_stack.contents.base_message_content import (
        BaseMessageContent,
    )
    from griptape.drivers.prompt.base_prompt_driver import StructuredOutputStrategy
    from griptape.tokenizers.base_tokenizer import BaseTokenizer
from rich.pretty import pprint  # will automatically nicely format things

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
        messages = self.__to_google_messages(prompt_stack)
        logger.debug(messages)
        params = self._base_params(prompt_stack)
        logger.debug((messages, params))
        response: GenerationResponse = self.client.generate_content(messages, **params)
        logger.debug(response.to_dict())
        usage_metadata = response.usage_metadata
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
    def try_stream(self, prompt_stack: PromptStack) -> Message:
        return Message(
            content="Stream not available for VertexAI", role=Message.ASSISTANT_ROLE
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
        return {
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
        # TODO: Add tools back in if necessary?

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

    # TODO: This is obsolete because I removed from try_run - How do I accurate make this reflect the results from VertexAI? Does it come back in parts?
    def __to_prompt_stack_message_content(self, content: Part) -> BaseMessageContent:
        # Only necessary if the information comes back in Parts, right now it is coming back in Text
        if content.text:
            return TextMessageContent(TextArtifact(content.text))
        else:
            raise ValueError(f"Unsupported message content type {content}")


if __name__ == "__main__":
    from google.oauth2.service_account import Credentials

    creds = os.environ["GOOGLE_CREDENTIALS"]

    schema = {
        "type": "object",
        "properties": {
            "description": {"type": "string"},
            "date": {"type": "integer"},
            "explanation": {"type": "string"},
        },
        "required": ["date", "description", "explanation"],
    }
    schema = None
    key_data = json.loads(creds)
    credentials = Credentials.from_service_account_info(key_data)
    test = VertexAIGooglePromptDriver(
        model="gemini-1.5-flash-002",
        project="griptape-cloud-dev",
        location="us-west1",
        credentials=credentials,
        response_schema=schema,
    )
    video_part = Part.from_uri(
        uri="gs://gt-airloom-video-analysis/back_entry-1733256720-1733256750.mp4",
        mime_type="video/mp4",
    )
    # Create PromptStack with the message
    prompt_stack = PromptStack()
    prompt_stack.add_user_message("Return the first instance of people")
    prompt_stack.add_message(
        role=Message.USER_ROLE, artifact=GenericArtifact(video_part)
    )  # Part is a generic type
    # prompt_stack.add_system_message("Use slang from the 1960s in your response")
    # for system_message in prompt_stack.system_messages:
    #     print(system_message.to_text())
    pprint(test.run(prompt_stack))

# Questions for collin:
# How do I get the system messages to work properly? How do I get output from running the vertexai driver to be properly logged?
# Why is it sometimes ignoring my system messages? Just an LLM thing?
# How would I input content like a uri and a text string like this:


# handle text and function separately - move logic to function to check for parts and try to copy/ make this logic similar
# # GenerationPart properties
# @property
# def text(self) -> str:
#     try:
#         return self.content.text
#     except (ValueError, AttributeError) as e:
#         # Enrich the error message with the whole Candidate.
#         # The Content object does not have full information.
#         raise ValueError(
#             "Cannot get the Candidate text.\n"
#             f"{e}\n"
#             "Candidate:\n" + _dict_to_pretty_string(self.to_dict())
#         ) from e

# @property
# def function_calls(self) -> Sequence["FunctionCall"]:
#     if not self.content or not self.content.parts:
#         return []
#     return [
#         part.function_call
#         for part in self.content.parts
#         if part._raw_part._pb.WhichOneof("data") == "function_call"
#     ]
