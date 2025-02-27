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

### Griptape Cloud

!!! info

    This driver requires the `drivers-observability-griptape-cloud` [extra](../index.md#extras).

The Griptape Cloud Observability Driver instruments `@observable` functions and methods with metrics and traces for use with the Griptape Cloud.

!!! note

    For the Griptape Cloud Observability Driver to function as intended, it must be run from within either a Managed Structure on Griptape Cloud
    or locally via the [Skatepark Emulator](https://github.com/griptape-ai/griptape-cli?tab=readme-ov-file#skatepark-emulator).

Here is an example of how to use the `GriptapeCloudObservabilityDriver` with the `Observability` context manager to send the telemetry to Griptape Cloud:
