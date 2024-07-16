from __future__ import annotations

import os
from typing import TYPE_CHECKING, Optional
from urllib.parse import urljoin
from uuid import UUID

import requests
from attrs import Attribute, Factory, define, field
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SpanExporter, SpanExportResult
from opentelemetry.sdk.util import ns_to_iso_str
from opentelemetry.trace import INVALID_SPAN, get_current_span

from griptape.drivers.observability.open_telemetry_observability_driver import OpenTelemetryObservabilityDriver

if TYPE_CHECKING:
    from collections.abc import Sequence

    from opentelemetry.sdk.trace import ReadableSpan, SpanProcessor


@define
class GriptapeCloudObservabilityDriver(OpenTelemetryObservabilityDriver):
    service_name: str = field(default="griptape-cloud", kw_only=True)
    base_url: str = field(
        default=Factory(lambda: os.getenv("GT_CLOUD_BASE_URL", "https://cloud.griptape.ai")), kw_only=True
    )
    api_key: str = field(default=Factory(lambda: os.getenv("GT_CLOUD_API_KEY")), kw_only=True)
    headers: dict = field(
        default=Factory(lambda self: {"Authorization": f"Bearer {self.api_key}"}, takes_self=True), kw_only=True
    )
    structure_run_id: str = field(default=Factory(lambda: os.getenv("GT_CLOUD_STRUCTURE_RUN_ID")), kw_only=True)
    span_processor: SpanProcessor = field(
        default=Factory(
            lambda self: BatchSpanProcessor(
                GriptapeCloudObservabilityDriver.SpanExporter(
                    base_url=self.base_url,
                    api_key=self.api_key,
                    headers=self.headers,
                    structure_run_id=self.structure_run_id,
                )
            ),
            takes_self=True,
        ),
        kw_only=True,
    )
    trace_provider: TracerProvider = field(default=Factory(lambda: TracerProvider()), kw_only=True)

    @staticmethod
    def format_trace_id(trace_id: int) -> str:
        return str(UUID(int=trace_id))

    @staticmethod
    def format_span_id(span_id: int) -> str:
        return str(UUID(int=span_id))

    @define
    class SpanExporter(SpanExporter):
        base_url: str = field(kw_only=True)
        api_key: str = field(kw_only=True)
        headers: dict = field(kw_only=True)
        structure_run_id: str = field(kw_only=True)

        def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
            url = urljoin(self.base_url.strip("/"), f"/api/structure-runs/{self.structure_run_id}/spans")
            payload = [
                {
                    "trace_id": GriptapeCloudObservabilityDriver.format_trace_id(span.context.trace_id),
                    "span_id": GriptapeCloudObservabilityDriver.format_span_id(span.context.span_id),
                    "parent_id": GriptapeCloudObservabilityDriver.format_span_id(span.parent.span_id)
                    if span.parent
                    else None,
                    "name": span.name,
                    "start_time": ns_to_iso_str(span.start_time) if span.start_time else None,
                    "end_time": ns_to_iso_str(span.end_time) if span.end_time else None,
                    "status": span.status.status_code.name,
                    "attributes": {**span.attributes} if span.attributes else {},
                    "events": [
                        {
                            "name": event.name,
                            "timestamp": ns_to_iso_str(event.timestamp) if event.timestamp else None,
                            "attributes": {**event.attributes} if event.attributes else {},
                        }
                        for event in span.events
                    ],
                }
                for span in spans
            ]
            response = requests.post(url=url, json=payload, headers=self.headers)
            return SpanExportResult.SUCCESS if response.status_code == 200 else SpanExportResult.FAILURE

    @structure_run_id.validator  # pyright: ignore[reportAttributeAccessIssue]
    def validate_run_id(self, _: Attribute, structure_run_id: str) -> None:
        if structure_run_id is None:
            raise ValueError(
                "structure_run_id must be set either in the constructor or as an environment variable (GT_CLOUD_STRUCTURE_RUN_ID)."
            )

    def get_span_id(self) -> Optional[str]:
        span = get_current_span()
        if span is INVALID_SPAN:
            return None
        return GriptapeCloudObservabilityDriver.format_span_id(span.get_span_context().span_id)
