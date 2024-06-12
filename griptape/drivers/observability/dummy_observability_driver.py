from griptape.drivers.observability.base_observability_driver import BaseObservabilityDriver


class DummyObservabilityDriver(BaseObservabilityDriver):
    def invoke_observable(self, func, instance, args, kwargs, decorator_args, decorator_kwargs):
        return func(*args, **kwargs)
