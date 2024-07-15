from __future__ import annotations

import logging
from abc import ABC
from typing import Callable

from attrs import define, field
from tenacity import Retrying, retry_if_not_exception_type, stop_after_attempt, wait_exponential


@define(slots=False)
class ExponentialBackoffMixin(ABC):
    min_retry_delay: float = field(default=2, kw_only=True)
    max_retry_delay: float = field(default=10, kw_only=True)
    max_attempts: int = field(default=10, kw_only=True)
    after_hook: Callable = field(default=lambda s: logging.warning(s), kw_only=True)
    ignored_exception_types: tuple[type[Exception], ...] = field(factory=tuple, kw_only=True)

    def retrying(self) -> Retrying:
        return Retrying(
            wait=wait_exponential(min=self.min_retry_delay, max=self.max_retry_delay),
            retry=retry_if_not_exception_type(self.ignored_exception_types),
            stop=stop_after_attempt(self.max_attempts),
            reraise=True,
            after=self.after_hook,
        )
