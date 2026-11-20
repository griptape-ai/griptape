from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from griptape.drivers.observability.open_telemetry import OpenTelemetryObservabilityDriver
from griptape.observability import Observability
from griptape.structures import Agent

observability_driver = OpenTelemetryObservabilityDriver(
    service_name="my-app", span_processor=BatchSpanProcessor(ConsoleSpanExporter())
)

with Observability(observability_driver=observability_driver):
    # Important! Only code within this block is subject to observability
    agent = Agent()
    agent.run("Name the five greatest rappers of all time")
