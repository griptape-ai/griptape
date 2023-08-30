import logging
from abc import ABC
from attr import define, field
from tenacity import Retrying, wait_exponential, stop_after_attempt


@define
class ExponentialBackoffMixin(ABC):
    min_retry_delay: float = field(default=2, kw_only=True)
    max_retry_delay: float = field(default=10, kw_only=True)
    max_attempts: int = field(default=10, kw_only=True)
    after_hook: callable = field(
        default=lambda s: logging.warning(s),
        kw_only=True
    )

    def retrying(self) -> Retrying:
        return Retrying(
            wait=wait_exponential(
                min=self.min_retry_delay,
                max=self.max_retry_delay
            ),
            stop=stop_after_attempt(self.max_attempts),
            reraise=True,
            after=self.after_hook,
        )
