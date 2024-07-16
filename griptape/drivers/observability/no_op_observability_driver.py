from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from attrs import define

from griptape.drivers import BaseObservabilityDriver

if TYPE_CHECKING:
    from griptape.common import Observable


@define
class NoOpObservabilityDriver(BaseObservabilityDriver):
    def observe(self, call: Observable.Call) -> Any:
        return call()

    def get_span_id(self) -> Optional[str]:
        return None
