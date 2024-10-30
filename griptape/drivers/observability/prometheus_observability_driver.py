from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Optional

from attrs import Attribute, Factory, define, field
from prometheus_client import Counter, Histogram

from griptape.drivers.observability.open_telemetry_observability_driver import OpenTelemetryObservabilityDriver
from griptape.utils.import_utils import import_optional_dependency

if TYPE_CHECKING:
    from opentelemetry.sdk.trace import SpanProcessor

    from griptape.common.observable import Observable


@define
class PrometheusObservabilityDriver(OpenTelemetryObservabilityDriver):
    span_processor: SpanProcessor = field(kw_only=True)
    request_count: Counter = field(init=False)
    request_duration: Histogram = field(init=False)

    @span_processor.validator
    def validate_span_processor(self, _: Attribute, span_processor: SpanProcessor) -> None:
        if span_processor is None:
            raise ValueError("span_processor must be provided.")

    def __attrs_post_init__(self) -> None:
        # Initialize the Prometheus metrics
        self.request_count = Counter(
            f"{self.service_name}_request_count",
            "Total number of requests",
            labelnames=['method'],
        )
        self.request_duration = Histogram(
            f"{self.service_name}_request_duration_seconds",
            "Duration of requests in seconds",
            labelnames=['method'],
        )
        super().__attrs_post_init__()  # Call to parent class initializer

    def observe(self, call: Observable.Call) -> Any:
        func = call.func
        instance = call.instance

        class_name = f"{instance.__class__.__name__}." if instance else ""
        method_name = f"{class_name}{func.__name__}()"

        # Start timing
        with self.request_duration.labels(method=method_name).time():
            # Increment the request count
            self.request_count.labels(method=method_name).inc()
            try:
                return call()
            except Exception as e:
                # Handle exceptions as needed
                raise e

    def get_span_id(self) -> Optional[str]:
        opentelemetry_trace = import_optional_dependency("opentelemetry.trace")
        span = opentelemetry_trace.get_current_span()
        if span is opentelemetry_trace.INVALID_SPAN:
            return None
        return str(span.get_span_context().span_id)  # Simple span ID formatting
