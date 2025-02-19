from __future__ import annotations

import logging
from io import BytesIO
from typing import TYPE_CHECKING

from attrs import define, field

from griptape.configs import Defaults
from griptape.drivers.embedding import BaseEmbeddingDriver
from griptape.utils import import_optional_dependency
from griptape.utils.decorators import lazy_property

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer


logger = logging.getLogger(Defaults.logging_config.logger_name)


@define
class HuggingFacePipelineEmbeddingDriver(BaseEmbeddingDriver):
    """Hugging Face Pipeline Embedding Driver.

    Attributes:
        model: Hugging Face Hub model name.
    """

    model: str = field(kw_only=True, metadata={"serializable": True})
    _sentence_transformer: SentenceTransformer = field(
        default=None, kw_only=True, alias="pipeline", metadata={"serializable": False}
    )

    @lazy_property()
    def sentence_transformer(self) -> SentenceTransformer:
        return import_optional_dependency("sentence_transformers").SentenceTransformer(self.model)

    def try_embed_chunk(self, chunk: str | bytes) -> list[float]:
        pil_image = import_optional_dependency("PIL.Image")

        return (
            self.sentence_transformer.encode(chunk)
            if isinstance(chunk, str)
            else self.sentence_transformer.encode(pil_image.open(BytesIO(chunk)))
        )
