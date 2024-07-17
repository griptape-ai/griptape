from attrs import Factory, define, field
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import SpanProcessor
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from griptape.drivers.observability.open_telemetry_observability_driver import OpenTelemetryObservabilityDriver


@define
class DatadogObservabilityDriver(OpenTelemetryObservabilityDriver):
    span_processor: SpanProcessor = field(
        default=Factory(
            lambda self: BatchSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4318/v1/traces")),
            takes_self=True,
        ),
        kw_only=True,
    )
