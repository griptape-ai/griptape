import atexit
import os

from griptape.utils.observability.griptape_cloud_span_exporter import GriptapeCloudSpanExporter
from griptape.utils.observability.griptape_instrumentor import GriptapeInstrumentor
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from opentelemetry.instrumentation.threading import ThreadingInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


class GriptapeCloudObservability:
    def __init__(self):
        self.trace_provider = None
        self.root_span_context_manager = None
        self.exit_handler = None

    def start(self):
        # 1. Configure griptape exporter
        resource = Resource(attributes={"service.name": "unknown"}, schema_url=None)
        self.trace_provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(self.trace_provider)
        self.trace_provider.add_span_processor(BatchSpanProcessor(GriptapeCloudSpanExporter()))

        # 2. Instrument library
        GriptapeInstrumentor().instrument(tracer_provider=self.trace_provider)
        ThreadingInstrumentor().instrument()

        # 3. Create a root span, named "main"
        tracer = trace.get_tracer("griptape", tracer_provider=self.trace_provider)
        self.root_span_context_manager = tracer.start_as_current_span("main")  # pyright: ignore
        self.root_span_context_manager.__enter__()
        trace.get_current_span().set_status(Status(StatusCode.OK))

        def exit_handler():
            if self.root_span_context_manager:
                self.root_span_context_manager.__exit__(None, None, None)
            if self.trace_provider:
                self.trace_provider.shutdown()

        self.exit_handler = exit_handler
        atexit.register(self.exit_handler)

    def finish(self):
        if self.exit_handler:
            atexit.unregister(self.exit_handler)
            self.exit_handler()

        ThreadingInstrumentor().uninstrument()
        GriptapeInstrumentor().uninstrument()


if os.environ.get("GT_CLOUD_OBSERVABILITY") == "True":
    if "GT_CLOUD_STRUCTURE_RUN_ID" not in os.environ:
        raise ValueError("GT_CLOUD_OBSERVABILITY requires GT_CLOUD_STRUCTURE_RUN_ID to be set")
    griptape_cloud_observability = GriptapeCloudObservability()
    griptape_cloud_observability.start()
