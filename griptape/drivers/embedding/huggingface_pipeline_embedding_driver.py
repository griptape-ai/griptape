from __future__ import annotations

import base64
import logging
from typing import TYPE_CHECKING

from attrs import define, field

from griptape.configs import Defaults
from griptape.drivers.embedding import BaseEmbeddingDriver
from griptape.utils import import_optional_dependency
from griptape.utils.decorators import lazy_property

if TYPE_CHECKING:
    from transformers import Pipeline


logger = logging.getLogger(Defaults.logging_config.logger_name)


@define
class HuggingFacePipelineEmbeddingDriver(BaseEmbeddingDriver):
    """Hugging Face Pipeline Embedding Driver.

    Attributes:
        model: Hugging Face Hub model name.
    """

    model: str = field(kw_only=True, metadata={"serializable": True})
    _pipeline: Pipeline = field(default=None, kw_only=True, alias="pipeline", metadata={"serializable": False})

    @lazy_property()
    def pipeline(self) -> Pipeline:
        return import_optional_dependency("transformers").pipeline(
            task="text-feature-extraction",
            model=self.model,
        )

    def try_embed_chunk(self, chunk: str | bytes) -> list[float]:
        response = self.pipeline(chunk) if isinstance(chunk, str) else self.pipeline(base64.b64encode(chunk).decode())

        return response[0][0]
