from __future__ import annotations

import os
from typing import TYPE_CHECKING

from attrs import Factory, define, field

from griptape.drivers.observability.open_telemetry_observability_driver import OpenTelemetryObservabilityDriver
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    from opentelemetry.sdk.trace import SpanProcessor


@define
class DatadogObservabilityDriver(OpenTelemetryObservabilityDriver):
    datadog_agent_endpoint: str = field(
        default=Factory(lambda: os.getenv("DD_AGENT_ENDPOINT", "http://localhost:4318")), kw_only=True
    )
    span_processor: SpanProcessor = field(
        default=Factory(
            lambda self: import_optional_dependency("opentelemetry.sdk.trace.export").BatchSpanProcessor(
                import_optional_dependency("opentelemetry.exporter.otlp.proto.http.trace_exporter").OTLPSpanExporter(
                    endpoint=f"{self.datadog_agent_endpoint}/v1/traces"
                )
            ),
            takes_self=True,
        ),
        kw_only=True,
    )
