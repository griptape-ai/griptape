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

from attrs import Attribute, Factory, define, field
from vertexai.generative_models import Part

from griptape.artifacts import TextArtifact
from griptape.common import Message, PromptStack, TextMessageContent, observable
from griptape.common.prompt_stack.contents.generic_message_content import GenericMessageContent
from griptape.common.prompt_stack.contents.image_message_content import ImageMessageContent
from griptape.configs import Defaults
from griptape.drivers.prompt.base_prompt_driver import BasePromptDriver
from griptape.tokenizers.vertexai_google_tokenizer import VertexAIGoogleTokenizer
from griptape.utils.decorators import lazy_property
from griptape.utils.import_utils import import_optional_dependency

if TYPE_CHECKING:
    from google.auth.credentials import Credentials
    from vertexai.generative_models import Content, GenerationResponse, GenerativeModel

    from griptape.common.prompt_stack.contents.base_message_content import BaseMessageContent
    from griptape.drivers.prompt.base_prompt_driver import StructuredOutputStrategy
    from griptape.tokenizers.base_tokenizer import BaseTokenizer


# need to install - pip install --upgrade google-cloud-aiplatform How do i do this?
logger = logging.getLogger(Defaults.logging_config.logger_name)
@define
class VertexAIGooglePromptDriver(BasePromptDriver):
    #Notes on attributes: Do google_application_credentials_content have to exist? should I require some other variable? 
    #Do I need all of these theoretically necessary attributes? Or should I remove the ones that don't matter to me.
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
    # These are all the fields for the VertexAI SDK
    google_application_credentials_content: str = field(default=None, kw_only=True, metadata={"serializable":False})
    project: str = field(default=None, kw_only=True, metadata={"serializable":True})
    location: str = field(default=None, kw_only=True, metadata={"serializable":True})
    response_schema: Optional[dict] = field(default=None, kw_only=True, metadata={"serializable": True})
    _credentials: Credentials = field(default=None, kw_only=True, alias="credentials", metadata={"serializable":False})

    # Necessary for Google Prompt Driver as well
    top_p: Optional[float] = field(default=None, kw_only=True, metadata={"serializable": True})
    top_k: Optional[int] = field(default=None, kw_only=True, metadata={"serializable": True})
    use_native_tools: bool = field(default=True, kw_only=True, metadata={"serializable":True})
    tokenizer: BaseTokenizer = field(
        # TODO: Do I need to add google_application_credential_content?
        default=Factory(
            lambda self: VertexAIGoogleTokenizer(model=self.model, project=self.project, location=self.location, credentials=self._credentials),
            takes_self=True,
        ),
        kw_only=True,
    )
    structured_output_strategy: StructuredOutputStrategy = field(default="tool",kw_only=True, metadata={"serializable":True})
    _client: GenerativeModel = field(default=None, kw_only=True, alias="client", metadata={"serializable":False})

    #Fields that might not be necessary
    encryption_spec_key_name: Optional[str] = field(default=None, kw_only=True, metadata={"serializable":False})
    service_account: Optional[str] = field(default=None, kw_only=True, metadata={"serializable":False})
    experiment: Optional[str] = field(default=None, kw_only=True, metadata={"serializable":True})
    staging_bucket: Optional[str] = field(default=None, kw_only=True, metadata={"serializable":True})

    #TODO: What is this for? structured output?
    @structured_output_strategy.validator  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
    def validate_structured_output_strategy(self, _: Attribute, value: str) -> str:
        if value == "native":
            raise ValueError(f"{__class__.__name__} does not support `{value}` structured output strategy.")

        return value

    # Get credentials for VertexAI
    @lazy_property()
    def credentials(self) -> Credentials:
        service_account = import_optional_dependency("google.oauth2.service_account")
        google_exceptions = import_optional_dependency("google.auth.exceptions")
        try:
            key_data = json.loads(self.google_application_credentials_content)
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
        return vertexai.generative_models.GenerativeModel(self.model)

    @observable
    def try_run(self, prompt_stack: PromptStack) -> Message:
        messages = self.__to_google_messages(prompt_stack)
        params = self._base_params(prompt_stack)
        logging.debug((messages,params))
        response: GenerationResponse = self.client.generate_content(messages, **params) #This should be the same and should be fine. Params are slightly different.
        logging.debug(response.to_dict())
        usage_metadata = response.usage_metadata
        return Message(
            content=response.text, #TODO: Google Prompt Driver was passing in a list of BaseMessages. How do I accomplish that with VertexAI?
            role=Message.ASSISTANT_ROLE,
            usage=Message.Usage(
                input_tokens= usage_metadata.prompt_token_count,
                output_tokens=usage_metadata.candidates_token_count
            )
        )

    # Streaming is not currently supported with VertexAI.
    @observable
    def try_stream(self, prompt_stack: PromptStack) -> Message:
        return Message(
            content="Stream not available for VertexAI",
            role=Message.ASSISTANT_ROLE
        )


    def _base_params(self, prompt_stack: PromptStack) -> dict:
        vertexai = import_optional_dependency("vertexai.generative_models")
        system_messages = prompt_stack.system_messages
        if system_messages:
            self.client._system_instruction = vertexai.Content(
                role="system",
                parts=[vertexai.Part.from_text(text=system_message.to_text()) for system_message in system_messages]
            )
        params = {
            "generation_config": vertexai.GenerationConfig(
                    temperature=self.temperature,
                    top_k = self.top_k,
                    top_p = self.top_p,
                    max_output_tokens=self.max_tokens,
                    response_schema=self.response_schema,
                    response_mime_type="application/json", #TODO: Allow this to be modified.
                    **self.extra_params)
        }
        #TODO: Add tools back in if necessary?
        return params

    # TODO: update return type to work accurately
    def __to_google_messages(self, prompt_stack:PromptStack) -> list[Content]: #TODO: Can't use ContentTypes - does this work?
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
        #TODO: How do Parts work - is this properly formatted given the constraints and the VertexAI SDK?
        if isinstance(content, TextMessageContent):
            return Part.from_text(content.artifact.to_text())
        elif isinstance(content, ImageMessageContent):
            return Part.from_data(mime_type=content.artifact.mime_type, data=content.artifact.value) #TODO: Check here for Image content
        elif isinstance(content, GenericMessageContent):
            return Part.from_uri(uri=content.artifact.value, mime_type=content.artifact.mime_type) #TODO: What do I do here in this case? This is incorrect.
        else:
            raise ValueError(f"Unsupported prompt stack content type: {type(content)}")

    #TODO: This is obsolete because I removed from try_run - How do I accurate make this reflect the results from VertexAI? Does it come back in parts?
    def __to_prompt_stack_message_content(self, content:Part) -> BaseMessageContent:
        if content.text:
            return TextMessageContent(TextArtifact(content.text))
        else:
            raise ValueError(f"Unsupported message content type {content}")



#TODO: How could I use this driver to add rules?
if __name__ == "__main__":

    creds = os.environ["GOOGLE_CREDENTIALS"]

    schema = {
            "type": "object",
            "properties": {
                "description": {"type": "string"},
                "date": {"type": "integer"},
                "explanation": {"type":"string"}
            },
            "required": ["date", "description", "explanation"],
        }
    test = VertexAIGooglePromptDriver(
        model="gemini-1.5-flash-002",
        project="griptape-cloud-dev",
        location="us-west1",
        google_application_credentials_content=creds,
        response_schema=schema)
    message = Message(
        role=Message.USER_ROLE,
        content="What is MLK day?",
    )
    message2 = Message(
        role=Message.USER_ROLE,
        content="What day is MLK day in 2025?"
    )
    message3 = Message(
        role=Message.USER_ROLE,
        content="Who is Malcom X?"
    )
    # Create PromptStack with the message
    #TODO: How should these be being processed / returned?
    prompt_stack = PromptStack(messages=[message,message2,message3])
    print(test.run(prompt_stack))

