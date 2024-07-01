from attrs import define
from griptape.common import Observable
from griptape.drivers import BaseObservabilityDriver
from typing import Any, Optional


@define
class NoOpObservabilityDriver(BaseObservabilityDriver):
    def observe(self, call: Observable.Call) -> Any:
        return call()

    def get_span_id(self) -> Optional[str]:
        return None
