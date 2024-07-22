from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from attrs import Factory, define, field

from griptape.drivers import BaseObservabilityDriver
from griptape.utils.import_utils import import_optional_dependency

if TYPE_CHECKING:
    from types import TracebackType

    from opentelemetry.sdk.trace import SpanProcessor, TracerProvider
    from opentelemetry.trace import Tracer

    from griptape.common import Observable


@define
class OpenTelemetryObservabilityDriver(BaseObservabilityDriver):
    service_name: str = field(default="griptape", kw_only=True)
    span_processor: SpanProcessor = field(kw_only=True)
    service_version: Optional[str] = field(default=None, kw_only=True)
    deployment_env: Optional[str] = field(default=None, kw_only=True)
    trace_provider: TracerProvider = field(
        default=Factory(
            lambda self: self._trace_provider_factory(),
            takes_self=True,
        ),
        kw_only=True,
    )
    _tracer: Optional[Tracer] = None
    _root_span_context_manager: Any = None

    def _trace_provider_factory(self) -> TracerProvider:
        opentelemetry_trace = import_optional_dependency("opentelemetry.sdk.trace")

        attributes = {"service.name": self.service_name}
        if self.service_version is not None:
            attributes["service.version"] = self.service_version
        if self.deployment_env is not None:
            attributes["deployment.environment"] = self.deployment_env
        return opentelemetry_trace.TracerProvider(
            resource=import_optional_dependency("opentelemetry.sdk.resources").Resource(attributes=attributes)
        )  # pyright: ignore[reportArgumentType]

    def __attrs_post_init__(self) -> None:
        opentelemetry_trace = import_optional_dependency("opentelemetry.trace")
        self.trace_provider.add_span_processor(self.span_processor)
        self._tracer = opentelemetry_trace.get_tracer(self.service_name, tracer_provider=self.trace_provider)

    def __enter__(self) -> None:
        opentelemetry_instrumentation_threading = import_optional_dependency("opentelemetry.instrumentation.threading")

        opentelemetry_instrumentation_threading.ThreadingInstrumentor().instrument()
        self._root_span_context_manager = self._tracer.start_as_current_span("main")  # pyright: ignore[reportCallIssue]
        self._root_span_context_manager.__enter__()

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        exc_traceback: Optional[TracebackType],
    ) -> bool:
        opentelemetry_trace = import_optional_dependency("opentelemetry.trace")
        opentelemetry_instrumentation_threading = import_optional_dependency("opentelemetry.instrumentation.threading")
        root_span = opentelemetry_trace.get_current_span()
        if exc_value:
            root_span = opentelemetry_trace.get_current_span()
            root_span.set_status(opentelemetry_trace.Status(opentelemetry_trace.StatusCode.ERROR))
            root_span.record_exception(exc_value)
        else:
            root_span.set_status(opentelemetry_trace.Status(opentelemetry_trace.StatusCode.OK))
        if self._root_span_context_manager:
            self._root_span_context_manager.__exit__(exc_type, exc_value, exc_traceback)
            self._root_span_context_manager = None
        self.trace_provider.force_flush()
        opentelemetry_instrumentation_threading.ThreadingInstrumentor().uninstrument()
        return False

    def observe(self, call: Observable.Call) -> Any:
        open_telemetry_trace = import_optional_dependency("opentelemetry.trace")
        func = call.func
        instance = call.instance
        tags = call.tags

        class_name = f"{instance.__class__.__name__}." if instance else ""
        span_name = f"{class_name}{func.__name__}()"
        with self._tracer.start_as_current_span(span_name) as span:  # pyright: ignore[reportCallIssue]
            if tags is not None:
                span.set_attribute("tags", tags)

            try:
                result = call()
                span.set_status(open_telemetry_trace.Status(open_telemetry_trace.StatusCode.OK))
                return result
            except Exception as e:
                span.set_status(open_telemetry_trace.Status(open_telemetry_trace.StatusCode.ERROR))
                span.record_exception(e)
                raise e

    def get_span_id(self) -> Optional[str]:
        opentelemetry_trace = import_optional_dependency("opentelemetry.trace")
        span = opentelemetry_trace.get_current_span()
        if span is opentelemetry_trace.INVALID_SPAN:
            return None
        return opentelemetry_trace.format_span_id(span.get_span_context().span_id)
