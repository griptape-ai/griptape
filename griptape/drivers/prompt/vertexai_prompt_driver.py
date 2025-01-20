# need google application credentials environment variable
# https://cloud.google.com/vertex-ai/docs/start/client-libraries
from __future__ import annotations

import json
import os
from typing import TYPE_CHECKING, Optional

from attrs import define, field
from google.auth.exceptions import MalformedError

from griptape.drivers.prompt.google_prompt_driver import GooglePromptDriver
from griptape.utils.decorators import lazy_property
from griptape.utils.import_utils import import_optional_dependency

if TYPE_CHECKING:
    from google.auth.credentials import Credentials
    from vertexai.generative_models import GenerativeModel

    from griptape.common import PromptStack


# need to install - pip install --upgrade google-cloud-aiplatform How do i do this?

@define
class VertexAIGooglePromptDriver(GooglePromptDriver):
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
    """
    # These are all the potential fields for the VertexAI SDK
    # Mandatory field to sign into vertex ai
    google_application_credentials_content: str = field(default=None, kw_only=True, metadata={"serializable":False})
    project: Optional[str] = field(default=None, kw_only=True, metadata={"serializable":True})
    location: Optional[str] = field(default=None, kw_only=True, metadata={"serializable":True})
    experiment: Optional[str] = field(default=None, kw_only=True, metadata={"serializable":True})
    staging_bucket: Optional[str] = field(default=None, kw_only=True, metadata={"serializable":True})
    _credentials: Credentials = field(default=None, kw_only=True, alias="credentials", metadata={"serializable":False})
    encryption_spec_key_name: Optional[str] = field(default=None, kw_only=True, metadata={"serializable":False})
    service_account: Optional[str] = field(default=None, kw_only=True, metadata={"serializable":False})
    _client: GenerativeModel = field(default=None, kw_only=True, alias="client", metadata={"serializable":False})

    # Get credentials for VertexAI
    @lazy_property()
    def credentials(self) -> Credentials:
        #TODO: Is this the proper way to do this?
        service_account = import_optional_dependency("google.oauth2.service_account")
        try:
            key_data = json.loads(self.google_application_credentials_content)
            print(key_data)
        except json.JSONDecodeError as e:
            errormsg = f"Credentials Improperly Formatted: {e}"
            print(errormsg)
            raise Exception(errormsg) from e
        try:
            credentials = service_account.Credentials.from_service_account_info(key_data)
        except MalformedError as e:
            errormsg = f"Credentials Improperly Formatted: {e}"
            raise Exception(errormsg) from e
        return credentials

    # Initialize VertexAI with proper credentials & values
    @lazy_property()
    def client(self) -> GenerativeModel:
        #TODO: Is this the proper way to do this?
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

    # TODO: Does VertexAI Gemini support the same parameters as the Gemini API?
    def _base_params(self, prompt_stack:PromptStack) -> dict:
        params = super()._base_params(prompt_stack)
        return params

if __name__ == "__main__":

    creds = "test"
    test = VertexAIGooglePromptDriver(
        model="gemini-1.5-flash-002",
        project="griptape-cloud-dev",
        location="us-west1",
        google_application_credentials_content=creds)
