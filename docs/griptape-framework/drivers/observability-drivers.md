# Observability Drivers

Observability Drivers are used by [Observability](../structures/observability.md) to send telemetry (metrics and traces) related to the execution of an LLM application. The telemetry can be used to monitor the application and to diagnose and troubleshoot issues. All Observability Drivers implement the following methods:

* `__enter__()` sets up the Driver.
* `__exit__()` tears down the Driver.
* `observe()` wraps all functions and methods marked with the `@observable` decorator. At a bare minimum, implementations call the wrapped function and return its result (a no-op). This enables the Driver to generate telemetry related to the invocation's call arguments, return values, exceptions, latency, etc.

## Griptape Cloud

The Griptape Cloud Observability Driver instruments `@observable` functions and methods with metrics and traces for use with the Griptape Cloud.

!!! note
    For the Griptape Cloud Observability Driver to function as intended, it must be run from within either a Managed Structure on Griptape Cloud,
    or locally via the [Skatepark Emulator](https://github.com/griptape-ai/griptape-cli?tab=readme-ov-file#skatepark-emulator).

Here is an example of how to use the `GriptapeCloudObservabilityDriver` with the `Observability` context manager to send the telemetry to Griptape Cloud:


```python title="PYTEST_IGNORE"
from griptape.drivers import GriptapeCloudObservabilityDriver
from griptape.rules import Rule
from griptape.structures import Agent
from griptape.observability import Observability

observability_driver = GriptapeCloudObservabilityDriver()

with Observability(observability_driver=observability_driver):
    agent = Agent(rules=[Rule("Output one word")])
    agent.run("Name an animal")
```


## OpenTelemetry

The [OpenTelemetry](https://opentelemetry.io/) Observability Driver instruments `@observable` functions and methods with metrics and traces for use with OpenTelemetry. You must configure a destination for the telemetry by providing a `SpanProcessor` to the Driver.

Here is an example of how to use the `OpenTelemetryObservabilityDriver` with the `Observability` context manager to output the telemetry directly to the console:

```python title="PYTEST_IGNORE"
from griptape.drivers import OpenTelemetryObservabilityDriver
from griptape.rules import Rule
from griptape.structures import Agent
from griptape.observability import Observability
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor

observability_driver = OpenTelemetryObservabilityDriver(
    service_name="my-gt-app",
    span_processor=BatchSpanProcessor(ConsoleSpanExporter())
)

with Observability(observability_driver=observability_driver):
    agent = Agent(rules=[Rule("Output one word")])
    agent.run("Name an animal")
```

Output (only relevant because of use of `ConsoleSpanExporter`):
```
[06/18/24 06:57:22] INFO     PromptTask 2d8ef95bf817480188ae2f74e754308a
                             Input: Name an animal
[06/18/24 06:57:23] INFO     PromptTask 2d8ef95bf817480188ae2f74e754308a
                             Output: Elephant
{
    "name": "Agent.before_run()",
    "context": {
        "trace_id": "0x4f3d72f7ff4e6a453f5c950fa097583e",
        "span_id": "0x8cf827b375f6922f",
        "trace_state": "[]"
    },
    "kind": "SpanKind.INTERNAL",
    "parent_id": "0x580276d16c584de3",
    "start_time": "2024-06-18T13:57:22.640040Z",
    "end_time": "2024-06-18T13:57:22.640822Z",
    "status": {
        "status_code": "OK"
    },
    "attributes": {},
    "events": [],
    "links": [],
    "resource": {
        "attributes": {
            "service.name": "my-gt-app"
        },
        "schema_url": ""
    }
}
{
    "name": "Agent.try_run()",
    "context": {
        "trace_id": "0x4f3d72f7ff4e6a453f5c950fa097583e",
        "span_id": "0x7191a27da608cbe7",
        "trace_state": "[]"
    },
    "kind": "SpanKind.INTERNAL",
    "parent_id": "0x580276d16c584de3",
    "start_time": "2024-06-18T13:57:22.640846Z",
    "end_time": "2024-06-18T13:57:23.287311Z",
    "status": {
        "status_code": "OK"
    },
    "attributes": {},
    "events": [],
    "links": [],
    "resource": {
        "attributes": {
            "service.name": "my-gt-app"
        },
        "schema_url": ""
    }
}
{
    "name": "Agent.after_run()",
    "context": {
        "trace_id": "0x4f3d72f7ff4e6a453f5c950fa097583e",
        "span_id": "0x99824dd1bc842f66",
        "trace_state": "[]"
    },
    "kind": "SpanKind.INTERNAL",
    "parent_id": "0x580276d16c584de3",
    "start_time": "2024-06-18T13:57:23.287707Z",
    "end_time": "2024-06-18T13:57:23.288666Z",
    "status": {
        "status_code": "OK"
    },
    "attributes": {},
    "events": [],
    "links": [],
    "resource": {
        "attributes": {
            "service.name": "my-gt-app"
        },
        "schema_url": ""
    }
}
{
    "name": "Agent.run()",
    "context": {
        "trace_id": "0x4f3d72f7ff4e6a453f5c950fa097583e",
        "span_id": "0x580276d16c584de3",
        "trace_state": "[]"
    },
    "kind": "SpanKind.INTERNAL",
    "parent_id": "0xa42d36d9fff76325",
    "start_time": "2024-06-18T13:57:22.640021Z",
    "end_time": "2024-06-18T13:57:23.288694Z",
    "status": {
        "status_code": "OK"
    },
    "attributes": {},
    "events": [],
    "links": [],
    "resource": {
        "attributes": {
            "service.name": "my-gt-app"
        },
        "schema_url": ""
    }
}
{
    "name": "main",
    "context": {
        "trace_id": "0x4f3d72f7ff4e6a453f5c950fa097583e",
        "span_id": "0xa42d36d9fff76325",
        "trace_state": "[]"
    },
    "kind": "SpanKind.INTERNAL",
    "parent_id": null,
    "start_time": "2024-06-18T13:57:22.607005Z",
    "end_time": "2024-06-18T13:57:23.288764Z",
    "status": {
        "status_code": "OK"
    },
    "attributes": {},
    "events": [],
    "links": [],
    "resource": {
        "attributes": {
            "service.name": "my-gt-app"
        },
        "schema_url": ""
    }
}
```


