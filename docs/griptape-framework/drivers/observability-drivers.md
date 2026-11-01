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

```python
--8<-- "docs/griptape-framework/drivers/src/observability_drivers_1.py"
```

### OpenTelemetry

!!! info

    This driver requires the `drivers-observability-opentelemetry` [extra](../index.md#extras).

The [OpenTelemetry](https://opentelemetry.io/) Observability Driver instruments `@observable` functions and methods with metrics and traces for use with OpenTelemetry. You must configure a destination for the telemetry by providing a `SpanProcessor` to the Driver.

Here is an example of how to use the `OpenTelemetryObservabilityDriver` with the `Observability` context manager to output the telemetry directly to the console:

```python
--8<-- "docs/griptape-framework/drivers/src/observability_drivers_2.py"
```

#### Prompt Driver metrics

To export metrics as well as traces, provide an OpenTelemetry SDK `MeterProvider` with configured metric readers. If `meter_provider` is omitted, the Driver uses OpenTelemetry's global meter provider. Without a configured meter provider, no metrics are exported and existing trace-only configurations continue to work.

```python
--8<-- "docs/griptape-framework/drivers/src/observability_drivers_3.py"
```

Each completed `PromptDriver.run()` records the following [GenAI metrics](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-metrics.md), including streaming calls:

| Metric                                            | Instrument | Unit      |
| ------------------------------------------------- | ---------- | --------- |
| `gen_ai.client.operation.duration`                | Histogram  | `s`       |
| `gen_ai.client.inference.usage.input_tokens`      | Counter    | `{token}` |
| `gen_ai.client.inference.usage.output_tokens`     | Counter    | `{token}` |
| `gen_ai.client.inference.operation.input_tokens`  | Histogram  | `{token}` |
| `gen_ai.client.inference.operation.output_tokens` | Histogram  | `{token}` |

Duration covers the complete Driver run, including any retries. A failed run records duration with `error.type` set to the exception's fully qualified class name. Token metrics use only the final successful response's reported usage, including the final cumulative usage of a stream. Usage from failed retry attempts is unavailable and is not counted. Missing or negative token counts are omitted; explicitly reported zero counts are preserved.

All metrics include `gen_ai.operation.name`, `gen_ai.provider.name`, and `gen_ai.request.model`. Built-in providers use the corresponding OpenTelemetry provider name when one is defined, and custom subclasses inherit their built-in provider's classification. Other custom Drivers use their class name as the provider and `chat` as the operation. Google uses `generate_content`; Hugging Face and SageMaker use `text_completion`. Token counters additionally include `gen_ai.token.modality="unknown"`, because Griptape's usage totals do not distinguish token modalities. Per-operation histograms do not include modality. Prompt and response content are not added to metric attributes.

The supplied `MeterProvider` is flushed when the Observability context exits, but is not shut down, allowing it to be reused. The caller owns its resource attributes, readers, exporters, and shutdown. The global meter provider's lifecycle remains managed by the application. Configure OpenTelemetry [Views](https://opentelemetry.io/docs/languages/python/instrumentation/#views) on the provider to customize histogram buckets; the GenAI conventions recommend duration buckets of `[0.01, 0.02, 0.04, 0.08, 0.16, 0.32, 0.64, 1.28, 2.56, 5.12, 10.24, 20.48, 40.96, 81.92]`.

These metrics do not measure streaming time to first chunk or per-chunk latency. The [token metric conventions](https://github.com/open-telemetry/semantic-conventions-genai/blob/main/docs/gen-ai/gen-ai-token-metrics.md) are currently in development.
