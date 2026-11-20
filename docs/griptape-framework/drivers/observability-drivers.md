---
search:
  boost: 2
---

## Overview

Observability Drivers are used by [Observability](../structures/observability.md) to send telemetry (metrics and traces) related to the execution of an LLM application. The telemetry can be used to monitor the application and to diagnose and troubleshoot issues. All Observability Drivers implement the following methods:

- `__enter__()` sets up the Driver.
- `__exit__()` tears down the Driver.
- `observe()` wraps all functions and methods marked with the `@observable` decorator. At a bare minimum, implementations call the wrapped function and return its result (a no-op). This enables the Driver to generate telemetry related to the invocation's call arguments, return values, exceptions, latency, etc.

## Observability Drivers

### OpenTelemetry

!!! info

    This driver requires the `drivers-observability-opentelemetry` [extra](../index.md#extras).

The [OpenTelemetry](https://opentelemetry.io/) Observability Driver instruments `@observable` functions and methods with metrics and traces for use with OpenTelemetry. You must configure a destination for the telemetry by providing a `SpanProcessor` to the Driver.

Here is an example of how to use the `OpenTelemetryObservabilityDriver` with the `Observability` context manager to output the telemetry directly to the console:

```python
--8<-- "docs/griptape-framework/drivers/src/observability_drivers_2.py"
```
