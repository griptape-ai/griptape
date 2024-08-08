import time

from griptape.common import observable
from griptape.drivers import GriptapeCloudObservabilityDriver
from griptape.observability import Observability


# Decorate a function
@observable
def my_function() -> None:
    time.sleep(3)


class MyClass:
    # Decorate a method
    @observable
    def my_method(self) -> None:
        time.sleep(1)
        my_function()
        time.sleep(2)


observability_driver = GriptapeCloudObservabilityDriver()

# When invoking the instrumented code from within the Observability context manager, the
# telemetry for the custom code will be sent to the destination specified by the driver.
with Observability(observability_driver=observability_driver):
    my_function()
    MyClass().my_method()
