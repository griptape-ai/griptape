from __future__ import annotations
from attrs import define, field, Factory
import openai

from griptape.drivers import OpenAiEmbeddingDriver


@define
class LmStudioEmbeddingDriver(OpenAiEmbeddingDriver):
    """
    Attributes:
        base_url: API URL. Defaults to LM Studio's v1 API URL.
        client: Optionally provide custom `openai.OpenAI` client.
    """

    base_url: str = field(default="http://localhost:1234/v1", kw_only=True, metadata={"serializable": True})
    client: openai.OpenAI = field(default=Factory(lambda self: openai.OpenAI(base_url=self.base_url), takes_self=True))
