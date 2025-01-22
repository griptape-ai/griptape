from __future__ import annotations

from typing import TYPE_CHECKING

from attrs import define, field

from griptape.tokenizers import BaseTokenizer
from griptape.utils import import_optional_dependency
from griptape.utils.decorators import lazy_property

if TYPE_CHECKING:
    from google.auth.credentials import Credentials
    from vertexai.generative_models import GenerativeModel


@define()
class VertexAIGoogleTokenizer(BaseTokenizer):
    MODEL_PREFIXES_TO_MAX_INPUT_TOKENS = {"gemini": 30720}
    MODEL_PREFIXES_TO_MAX_OUTPUT_TOKENS = {"gemini": 2048}

    #TODO: Do I need to add all of the other possible fields for the VertexAI SDK? 
    project: str = field(default=None, kw_only=True,metadata={"serializable": False})
    location: str = field(default=None, kw_only=True, metadata={"serializable":False})
    credentials: Credentials = field(default=None, kw_only=True, alias="credentials", metadata={"serializable":False}) 
    _client: GenerativeModel = field(default=None, kw_only=True, alias="client", metadata={"serializable": False})

    @lazy_property()
    def client(self) -> GenerativeModel:
        import_optional_dependency("google.cloud.aiplatform")
        vertexai = import_optional_dependency("vertexai")
        vertexai.init(
            project=self.project,
            location=self.location,
            credentials=self.credentials,

        )
        return vertexai.generative_models.GenerativeModel(self.model)

    def count_tokens(self, text: str) -> int:
        return self.client.count_tokens(text).total_tokens
