from __future__ import annotations
import logging
import time
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from tenacity import Retrying, wait_exponential, after_log
from attr import define, field
from griptape.tokenizers import BaseTokenizer

if TYPE_CHECKING:
    from griptape.artifacts import TextArtifact


@define
class BasePromptDriver(ABC):
    min_retry_delay: float = field(default=2, kw_only=True)
    max_retry_delay: float = field(default=10, kw_only=True)
    
    temperature: float = field(default=0.1, kw_only=True)
    model: str
    tokenizer: BaseTokenizer

    def run(self, **kwargs) -> TextArtifact:
        for attempt in Retrying(
            wait=wait_exponential(
                min=self.min_retry_delay,
                max=self.max_retry_delay
            ),
            reraise=True,
            after=after_log(
                logger=logging.getLogger(__name__),
                log_level=logging.ERROR
            ),
        ):
            with attempt:
                return self.try_run(**kwargs)

    @abstractmethod
    def try_run(self, **kwargs) -> TextArtifact:
        ...
