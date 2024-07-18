import os

from attrs import Factory, define, field
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import SpanProcessor
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from griptape.drivers.observability.open_telemetry_observability_driver import OpenTelemetryObservabilityDriver


@define
class DatadogObservabilityDriver(OpenTelemetryObservabilityDriver):
    datadog_agent_endpoint: str = field(
        default=Factory(lambda: os.getenv("DD_AGENT_ENDPOINT", "http://localhost:4318/v1/traces")), kw_only=True
    )
    span_processor: SpanProcessor = field(
        default=Factory(
            lambda self: BatchSpanProcessor(OTLPSpanExporter(endpoint=self.datadog_agent_endpoint)),
            takes_self=True,
        ),
        kw_only=True,
    )
