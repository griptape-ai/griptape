from typing import Optional
from attrs import define, field
from griptape.drivers.observability.base_observability_driver import BaseObservabilityDriver
from griptape.drivers.observability.dummy_observability_driver import DummyObservabilityDriver

_dummy_observability_driver = DummyObservabilityDriver()
_global_observability_driver: Optional[BaseObservabilityDriver] = None


@define
class Observability:
    driver: BaseObservabilityDriver = field(kw_only=True)

    @staticmethod
    def get_global_driver() -> Optional[BaseObservabilityDriver]:
        global _global_observability_driver
        return _global_observability_driver

    @staticmethod
    def set_global_driver(driver: Optional[BaseObservabilityDriver]):
        global _global_observability_driver
        _global_observability_driver = driver

    @staticmethod
    def invoke_observable(func, instance, args, kwargs, decorator_args, decorator_kwargs):
        driver = Observability.get_global_driver() or _dummy_observability_driver
        return driver.invoke_observable(func, instance, args, kwargs, decorator_args, decorator_kwargs)

    def __enter__(self):
        if Observability.get_global_driver() is not None:
            raise ValueError("Observability driver already set.")
        Observability.set_global_driver(self.driver)
        self.driver.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        Observability.set_global_driver(None)
        self.driver.__exit__(exc_type, exc_value, traceback)
        return False
