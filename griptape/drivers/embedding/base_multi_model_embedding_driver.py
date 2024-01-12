from __future__ import annotations
from abc import ABC
from typing import TYPE_CHECKING, Optional

from attr import define, field

from griptape.drivers import BaseEmbeddingDriver

if TYPE_CHECKING:
    from griptape.drivers import BaseEmbeddingModelDriver


@define
class BaseMultiModelEmbeddingDriver(BaseEmbeddingDriver, ABC):
    embedding_model_driver: BaseEmbeddingModelDriver = field(kw_only=True)
