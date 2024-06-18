import os

from attrs import define, Factory, field
from griptape.drivers.observability.open_telemetry_observability_driver import OpenTelemetryObservabilityDriver
from opentelemetry.sdk.trace import SpanProcessor
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
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
                OTLPSpanExporter(
                    endpoint=urljoin(self.base_url.strip("/"), f"/api/structure-runs/{self.structure_run_id}/spans"),
                    headers=self.headers,
                )
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
