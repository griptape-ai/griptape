---
search:
  boost: 2 
---

## Overview

The [Observability](../../reference/griptape/observability/observability.md) context manager sends telemetry (metrics and traces) for all functions and methods annotated with the `@observable` decorator to a destination of your choice. This is useful for monitoring and debugging your application.

Observability is completely optional. To opt in, wrap your application code with the [Observability](../../reference/griptape/observability/observability.md) context manager, for example:

```python
--8<-- "docs/griptape-framework/structures/src/observability_1.py"
```

!!! info
    For available Drivers (and destinations), see [Observability Drivers](../drivers/observability-drivers.md).

## Tracing Custom Code

All functions and methods annotated with the `@observable` decorator will be traced when invoked within the context of the [Observability](../../reference/griptape/observability/observability.md) context manager, including functions and methods defined outside of the Griptape framework. Thus to trace custom code, you just need to add the `@observable` decorator to your function or method, then invoke it within the [Observability](../../reference/griptape/observability/observability.md) context manager.

For example:

```python
--8<-- "docs/griptape-framework/structures/src/observability_2.py"
```
