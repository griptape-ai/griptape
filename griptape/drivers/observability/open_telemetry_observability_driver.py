from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from attrs import Factory, define, field
from opentelemetry.instrumentation.threading import ThreadingInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import SpanProcessor, TracerProvider
from opentelemetry.trace import INVALID_SPAN, Status, StatusCode, Tracer, format_span_id, get_current_span, get_tracer

from griptape.drivers import BaseObservabilityDriver

if TYPE_CHECKING:
    from types import TracebackType

    from griptape.common import Observable


@define
class OpenTelemetryObservabilityDriver(BaseObservabilityDriver):
    service_name: str = field(kw_only=True)
    span_processor: SpanProcessor = field(kw_only=True)
    trace_provider: TracerProvider = field(
        default=Factory(
            lambda self: TracerProvider(resource=Resource(attributes={"service.name": self.service_name})),
            takes_self=True,
        ),
        kw_only=True,
    )
    _tracer: Optional[Tracer] = None
    _root_span_context_manager: Any = None

    def __attrs_post_init__(self) -> None:
        self.trace_provider.add_span_processor(self.span_processor)
        self._tracer = get_tracer(self.service_name, tracer_provider=self.trace_provider)

    def __enter__(self) -> None:
        ThreadingInstrumentor().instrument()
        self._root_span_context_manager = self._tracer.start_as_current_span("main")  # pyright: ignore[reportCallIssue]
        self._root_span_context_manager.__enter__()

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        exc_traceback: Optional[TracebackType],
    ) -> bool:
        root_span = get_current_span()
        if exc_value:
            root_span = get_current_span()
            root_span.set_status(Status(StatusCode.ERROR))
            root_span.record_exception(exc_value)
        else:
            root_span.set_status(Status(StatusCode.OK))
        if self._root_span_context_manager:
            self._root_span_context_manager.__exit__(exc_type, exc_value, exc_traceback)
            self._root_span_context_manager = None
        self.trace_provider.force_flush()
        ThreadingInstrumentor().uninstrument()
        return False

    def observe(self, call: Observable.Call) -> Any:
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
                span.set_status(Status(StatusCode.OK))
                return result
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR))
                span.record_exception(e)
                raise e

    def get_span_id(self) -> Optional[str]:
        span = get_current_span()
        if span is INVALID_SPAN:
            return None
        return format_span_id(span.get_span_context().span_id)
