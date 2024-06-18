## Overview

You can use [Observability](../../reference/griptape/observability/observability.md) context manager to send telemetry (metrics and traces) for all functions and methods annotated with the `@observable` decorator to a destination of your choice. This is useful for monitoring and debugging your application.

Observability is completely optional. You can opt in to using it by providing an `ObservabilityDriver` to the `Observability` context manager, for example:

```python title="PYTEST_IGNORE"
from griptape.drivers import BaseObservabilityDriver
from griptape.rules import Rule
from griptape.structures import Agent
from griptape.observability import Observability

driver: BaseObservabilityDriver = ... # Your choice of driver

with Observability(driver=driver):
    # Your code here
    # Important! Only code within this block will be instrumented
```

For available drivers, see [Observability Drivers](../drivers/observability-drivers.md).

## Tracing Custom Code

All functions and methods annotated with the `@observable` decorator will be traced by default. If you want to trace custom code, you can use the `@observable` decorator.

For example:

```python title="PYTEST_IGNORE"
import time
from griptape.observability import observable
from griptape.drivers import BaseObservabilityDriver
from griptape.rules import Rule
from griptape.structures import Agent
from griptape.observability import Observability

# Decorate a function
@observable
def my_function():
    time.sleep(3)

class MyClass:
    # Decorate a method
    @observable
    def my_method(self):
        time.sleep(1)
        my_function()
        time.sleep(2)

driver: BaseObservabilityDriver = ... # Your choice of driver

# When invoking the instrumented code from within the Observability context manager, the
# telemetry for the custom code will be sent to the destination specified by the driver.
with Observability(driver=driver):
    my_function()
    MyClass().my_method()
```