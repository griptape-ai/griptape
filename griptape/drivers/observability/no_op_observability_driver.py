from attrs import define
from griptape.common import Observable
from griptape.drivers import BaseObservabilityDriver
from typing import Any


@define
class NoOpObservabilityDriver(BaseObservabilityDriver):
    def observe(self, call: Observable.Call) -> Any:
        return call()
