import os
from collections.abc import Sequence
from urllib.parse import urljoin
from typing_extensions import override
from attrs import Factory, define, field
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter


@define
class GriptapeCloudSpanExporter(SpanExporter):
    base_url: str = field(
        default=Factory(lambda: os.getenv("GT_CLOUD_BASE_URL", "https://cloud.griptape.ai")), kw_only=True
    )
    api_key: str = field(default=Factory(lambda: os.getenv("GT_CLOUD_API_KEY")), kw_only=True)
    headers: dict = field(
        default=Factory(lambda self: {"Authorization": f"Bearer {self.api_key}"}, takes_self=True), kw_only=True
    )
    structure_run_id: str = field(default=Factory(lambda: os.getenv("GT_CLOUD_STRUCTURE_RUN_ID")), kw_only=True)
    _underlying: SpanExporter = field(
        default=Factory(
            lambda self: OTLPSpanExporter(
                endpoint=urljoin(self.base_url.strip("/"), f"/api/structure-runs/{self.structure_run_id}/spans"),
                headers=self.headers,
            ),
            takes_self=True,
        ),
        kw_only=True,
    )

    @structure_run_id.validator  # pyright: ignore
    def validate_run_id(self, _, structure_run_id: str):
        if structure_run_id is None:
            raise ValueError(
                "structure_run_id must be set either in the constructor or as an environment variable (GT_CLOUD_STRUCTURE_RUN_ID)."
            )

    @override
    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        return self._underlying.export(spans)

    @override
    def shutdown(self):
        self._underlying.shutdown()

    @override
    def force_flush(self, timeout_millis: int = 30000) -> bool:
        return self._underlying.force_flush(timeout_millis)
