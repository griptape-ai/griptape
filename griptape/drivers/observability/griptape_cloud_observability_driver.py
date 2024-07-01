import os
import requests

from collections.abc import Sequence

from attrs import define, Factory, field
from griptape.drivers.observability.open_telemetry_observability_driver import OpenTelemetryObservabilityDriver
from opentelemetry.trace import format_trace_id, format_span_id
from opentelemetry.sdk.trace import SpanProcessor, ReadableSpan
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SpanExporter, SpanExportResult
from opentelemetry.sdk.util import ns_to_iso_str
from urllib.parse import urljoin


@define
class GriptapeCloudObservabilityDriver(OpenTelemetryObservabilityDriver):
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
                    "trace_id": format_trace_id(span.context.trace_id),
                    "span_id": format_span_id(span.context.span_id),
                    "parent_id": format_span_id(span.parent.span_id) if span.parent else None,
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

    @structure_run_id.validator  # pyright: ignore
    def validate_run_id(self, _, structure_run_id: str):
        if structure_run_id is None:
            raise ValueError(
                "structure_run_id must be set either in the constructor or as an environment variable (GT_CLOUD_STRUCTURE_RUN_ID)."
            )
