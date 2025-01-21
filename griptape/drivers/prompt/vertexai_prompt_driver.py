# need google application credentials environment variable
# https://cloud.google.com/vertex-ai/docs/start/client-libraries
#https://cloud.google.com/python/docs/reference/aiplatform/latest
#https://cloud.google.com/python/docs/reference/aiplatform/latest?hl=en
#https://cloud.google.com/vertex-ai/generative-ai/docs/reference/python/latest/vertexai.preview.generative_models.GenerativeModel


# Google gemini doesn't work with the old version of parts and whatnot - needs it's own implementation
from __future__ import annotations

import json
import logging
import os
from typing import TYPE_CHECKING, Optional

from attrs import Factory, define, field, Attribute
from google.generativeai.types import ContentDict
from vertexai.generative_models import Part, GenerationResponse

from griptape.artifacts import TextArtifact
from griptape.common import Message, PromptStack, TextMessageContent, observable
from griptape.common.prompt_stack.contents.base_message_content import BaseMessageContent
from griptape.common.prompt_stack.contents.generic_message_content import GenericMessageContent
from griptape.common.prompt_stack.contents.image_message_content import ImageMessageContent
from griptape.configs import Defaults
from griptape.drivers.prompt.base_prompt_driver import BasePromptDriver
from griptape.drivers.prompt.google_prompt_driver import GooglePromptDriver
from griptape.tokenizers.base_tokenizer import BaseTokenizer
from griptape.tokenizers.google_tokenizer import GoogleTokenizer
from griptape.tokenizers.vertexai_google_tokenizer import VertexAiGoogleTokenizer
from griptape.utils.decorators import lazy_property
from griptape.utils.import_utils import import_optional_dependency

if TYPE_CHECKING:
    from google.auth.credentials import Credentials
    from vertexai.generative_models import GenerativeModel, Part, Content
    from vertexai.generative_models._generative_models import ContentDict

    from griptape.common import PromptStack
    from griptape.drivers.prompt.base_prompt_driver import StructuredOutputStrategy


# need to install - pip install --upgrade google-cloud-aiplatform How do i do this?
logger = logging.getLogger(Defaults.logging_config.logger_name)
@define
class VertexAIGooglePromptDriver(BasePromptDriver):
    """Vertex AI Google Prompt Driver.

    Attributes:
        google_application_credentials_content: str
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
    # These are all the potential fields for the VertexAI SDK
    # Mandatory field to sign into vertex ai
    google_application_credentials_content: str = field(default=None, kw_only=True, metadata={"serializable":False})
    project: str = field(default=None, kw_only=True, metadata={"serializable":True})
    location: str = field(default=None, kw_only=True, metadata={"serializable":True})
    experiment: Optional[str] = field(default=None, kw_only=True, metadata={"serializable":True}) #do i need this one
    staging_bucket: Optional[str] = field(default=None, kw_only=True, metadata={"serializable":True}) #do i need this one
    tokenizer: BaseTokenizer = field(
        default=Factory(
            lambda self: VertexAiGoogleTokenizer(model=self.model, project=self.project, location=self.location),
            takes_self=True,
        ),
        kw_only=True,
    )
    _credentials: Credentials = field(default=None, kw_only=True, alias="credentials", metadata={"serializable":False}) 
    encryption_spec_key_name: Optional[str] = field(default=None, kw_only=True, metadata={"serializable":False}) #do i need this one
    service_account: Optional[str] = field(default=None, kw_only=True, metadata={"serializable":False}) #do i need this one
    top_p: Optional[float] = field(default=None, kw_only=True, metadata={"serializable": True})
    top_k: Optional[int] = field(default=None, kw_only=True, metadata={"serializable": True})
    use_native_tools: bool = field(default=True, kw_only=True, metadata={"serializable":True})
    structured_output_strategy: StructuredOutputStrategy = field(default="tool",kw_only=True, metadata={"serializable":True})
    _client: GenerativeModel = field(default=None, kw_only=True, alias="client", metadata={"serializable":False})

    @structured_output_strategy.validator  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
    def validate_structured_output_strategy(self, _: Attribute, value: str) -> str:
        if value == "native":
            raise ValueError(f"{__class__.__name__} does not support `{value}` structured output strategy.")

        return value
    # Get credentials for VertexAI
    @lazy_property()
    def credentials(self) -> Credentials:
        #TODO: Is this the proper way to do this?
        service_account = import_optional_dependency("google.oauth2.service_account")
        google_exceptions = import_optional_dependency("google.auth.exceptions")
        try:
            key_data = json.loads(self.google_application_credentials_content)
            logging.debug(key_data)
        except json.JSONDecodeError as e:
            errormsg = f"Credentials Improperly Formatted: {e}"
            logging.debug(errormsg)
            raise Exception(errormsg) from e
        try:
            credentials = service_account.Credentials.from_service_account_info(key_data)
        except google_exceptions.MalformedError as e:
            errormsg = f"Credentials Improperly Formatted: {e}"
            raise Exception(errormsg) from e
        return credentials

    # Initialize VertexAI with proper credentials & values
    @lazy_property()
    def client(self) -> GenerativeModel:
        #TODO: Is this the proper way to do this?
        import_optional_dependency("google.cloud.aiplatform")
        vertexai = import_optional_dependency("vertexai")
        vertexai.init(
            project=self.project,
            location=self.location,
            experiment=self.experiment,
            staging_bucket=self.staging_bucket,
            credentials=self.credentials, # Should be already established from other "lazy" property.
            encryption_spec_key_name=self.encryption_spec_key_name,
            service_account=self.service_account,
        )
        #TODO: is this vertexai.generative_models.GenerativeModel
        return vertexai.generative_models.GenerativeModel(self.model)

    @observable
    def try_run(self, prompt_stack: PromptStack) -> Message:
        messages = self.__to_google_messages(prompt_stack) #TODO: initialize this function
        params = self._base_params(prompt_stack)
        logging.debug((messages,params)) #TBD I don't htink it even got to this point.
        response: GenerationResponse = self.client.generate_content(messages, **params) #This should be the same and should be fine. Params are slightly different.
        logging.debug(response.to_dict())
        usage_metadata = response.usage_metadata
        return Message(
            content=response.text,
            role=Message.ASSISTANT_ROLE,
            usage=Message.Usage(
                input_tokens= usage_metadata.prompt_token_count,
                output_tokens=usage_metadata.candidates_token_count
            )
        )

    @observable
    def try_stream(self, prompt_stack: PromptStack) -> Message:
        return Message(
            content="Stream not available for VertexAI",
            role=Message.ASSISTANT_ROLE
        )


    # TODO: Does VertexAI Gemini support the same parameters as the Gemini API?
    def _base_params(self, prompt_stack: PromptStack) -> dict:
        vertexai = import_optional_dependency("vertexai.generative_models")
        system_messages = prompt_stack.system_messages
        if system_messages:
            self.client._system_instruction = vertexai.Content(
                role="system",
                parts=[vertexai.Part.from_text(text=system_message.to_text()) for system_message in system_messages]
            )
        params = {
            # todo: add response schema
            # stop_sequences not present because 'stream' is not allowed.
            "generation_config":
                {
                        "max_output_tokens": self.max_tokens,
                        "temperature": self.temperature,
                        "top_p": self.top_p,
                        "top_k": self.top_k,
                        **self.extra_params,
                }
        }
        #TODO: add tools back in if necessary
        return params

    # TODO: update return type to work accurately
    def __to_google_messages(self, prompt_stack:PromptStack) -> list[Content]:
        content = import_optional_dependency("vertexai.generative_models")
        return [
            content.Content(
                role = self.__to_google_role(message),
                parts = [self.__to_google_message_content(content) for content in message.content]
            )
            for message in prompt_stack.messages
            if not message.is_system()
        ]

    def __to_google_role(self, message:Message) -> str:
        if message.is_assistant():
            return "model"
        else:
            return "user"

    def __to_google_message_content(self, content: BaseMessageContent) -> Content | Part | str:
        #TODO: Determine the right solution for URI! 
        if isinstance(content, TextMessageContent):
            return Part.from_text(content.artifact.to_text())
        elif isinstance(content, ImageMessageContent):
            return Part.from_data(mime_type=content.artifact.mime_type, data=content.artifact.value)
        elif isinstance(content, GenericMessageContent):
            return Part.from_uri(uri=content.artifact.value, mime_type=content.artifact.mime_type) #TODO: What do I do here in this case?
        else:
            raise ValueError(f"Unsupported prompt stack content type: {type(content)}")

    def __to_prompt_stack_message_content(self, content:Part) -> BaseMessageContent:
        if content.text:
            return TextMessageContent(TextArtifact(content.text))
        else:
            raise ValueError(f"Unsupported message content type {content}")

if __name__ == "__main__":

    creds = os.environ["GOOGLE_CREDENTIALS"]
    test = VertexAIGooglePromptDriver(
        model="gemini-1.5-flash-002",
        project="griptape-cloud-dev",
        location="us-west1",
        google_application_credentials_content=creds)
    message = Message(
        role=Message.USER_ROLE,
        content="What is MLK day?"
    )
    # Create PromptStack with the message
    prompt_stack = PromptStack(messages=[message])
    print(test.try_run(prompt_stack))

