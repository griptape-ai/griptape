from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from griptape.drivers import OpenTelemetryObservabilityDriver
from griptape.observability import Observability
from griptape.rules import Rule
from griptape.structures import Agent

observability_driver = OpenTelemetryObservabilityDriver(
    service_name="name-an-animal", span_processor=BatchSpanProcessor(ConsoleSpanExporter())
)

with Observability(observability_driver=observability_driver):
    agent = Agent(rules=[Rule("Output one word")])
    agent.run("Name an animal")
