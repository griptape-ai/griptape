from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from griptape.drivers.observability.open_telemetry import OpenTelemetryObservabilityDriver
from griptape.observability import Observability
from griptape.structures import Agent

meter_provider = MeterProvider(
    resource=Resource.create({"service.name": "name-an-animal"}),
    metric_readers=[PeriodicExportingMetricReader(ConsoleMetricExporter())],
)
try:
    observability_driver = OpenTelemetryObservabilityDriver(
        service_name="name-an-animal",
        span_processor=BatchSpanProcessor(ConsoleSpanExporter()),
        meter_provider=meter_provider,
    )
    with Observability(observability_driver=observability_driver):
        Agent().run("Name an animal")
finally:
    meter_provider.shutdown()
