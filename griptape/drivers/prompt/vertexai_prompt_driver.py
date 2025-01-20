# need google application credentials environment variable
# https://cloud.google.com/vertex-ai/docs/start/client-libraries

from typing import TYPE_CHECKING, Optional
from attrs import define, field
import vertexai

from griptape.drivers.prompt.google_prompt_driver import GooglePromptDriver
from griptape.utils.decorators import lazy_property
from griptape.utils.import_utils import import_optional_dependency


if TYPE_CHECKING:
    from google.auth.credentials import Credentials
    from vertexai.generative_models import GenerativeModel, Part

    from griptape.common import PromptStack


# need to install - pip install --upgrade google-cloud-aiplatform How do i do this?

@define
class VertexAIGooglePromptDriver(GooglePromptDriver):
    """Vertex AI Google Prompt Driver.

    project: str
    location: str
    experiment: str
    staging_bucket: str
    credentials: google.auth.credentials.Credentials
    encryption_spec_key_name: str
    service_account: str
    
    Attributes:
        api_key: Google API key.
        model: Google model name.
        client: Custom `GenerativeModel` client.
        top_p: Optional value for top_p.
        top_k: Optional value for top_k.
    """
    # These are all the potential fields for the VertexAI SDK
    project: Optional[str] = field(default=None, kw_only=True, metadata={"serializable":True})
    location: Optional[str] = field(default=None, kw_only=True, metadata={"serializable":True})
    experiment: Optional[str] = field(default=None, kw_only=True, metadata={"serializable":True})
    staging_bucket: Optional[str] = field(default=None, kw_only=True, metadata={"serializable":True})
    credentials: Optional[Credentials] = field(default=None, kw_only=True, metadata={"serializable":False})
    encryption_spec_key_name: Optional[str] = field(default=None, kw_only=True, metadata={"serializable":False})
    service_account: Optional[str] = field(default=None, kw_only=True, metadata={"serializable":False})
    _client: GenerativeModel = field(default=None, kw_only=True, alias="client", metadata={"serializable":False}) #TODO: What could this be 

    @lazy_property()
    def client(self) -> GenerativeModel:
        #TODO: Will this work in the same way as the google one does
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
        return vertexai.generative_models.GenerativeModel(self.model)

    def _base_params(self, prompt_stack:PromptStack) -> dict:
        params = super()._base_params(prompt_stack)
        vertex_ai = import_optional_dependency("vertexai")
        models = import_optional_dependency("vertexai.generative_models")


    # TODO: Could be perfectly reasonable to pass a photo, video, and prompt.