import os
import re
from unittest.mock import MagicMock
import pytest
from griptape.utils.observability.griptape_cloud_span_exporter import GriptapeCloudSpanExporter


class TestGriptapeSpanExporter:
    @pytest.fixture
    def mock_otlp_span_exporter_class(self, mocker):
        return mocker.patch("griptape.utils.observability.griptape_cloud_span_exporter.OTLPSpanExporter")

    @pytest.fixture
    def mock_otlp_span_exporter(self, mock_otlp_span_exporter_class):
        return mock_otlp_span_exporter_class.return_value

    @pytest.fixture(autouse=True)
    def cleanup(self):
        keys = ["GT_CLOUD_STRUCTURE_RUN_ID", "GT_CLOUD_API_KEY", "GT_CLOUD_BASE_URL"]
        old_values = {key: os.environ.get(key) for key in keys}

        yield

        for key, value in old_values.items():
            if value is not None:
                os.environ[key] = value
            else:
                os.environ.pop(key, None)

    def test_init(self, mock_otlp_span_exporter_class, mock_otlp_span_exporter):
        os.environ["GT_CLOUD_STRUCTURE_RUN_ID"] = "test_structure_run_id"
        os.environ["GT_CLOUD_API_KEY"] = "secret"
        os.environ.pop("GT_CLOUD_BASE_URL", None)
        exporter = GriptapeCloudSpanExporter()
        assert exporter.base_url == "https://cloud.griptape.ai"
        assert exporter.api_key == "secret"
        assert exporter.structure_run_id == "test_structure_run_id"
        assert exporter._underlying == mock_otlp_span_exporter
        mock_otlp_span_exporter_class.assert_called_once_with(
            endpoint="https://cloud.griptape.ai/api/structure-runs/test_structure_run_id/spans",
            headers={"Authorization": "Bearer secret"},
        )

    def test_init_raises_when_structure_run_id_is_none(self):
        with pytest.raises(ValueError) as e:
            GriptapeCloudSpanExporter()
        assert e.match(
            re.escape(
                "structure_run_id must be set either in the constructor or as an environment variable (GT_CLOUD_STRUCTURE_RUN_ID)."
            )
        )

    def test_export(self, mock_otlp_span_exporter):
        os.environ["GT_CLOUD_STRUCTURE_RUN_ID"] = "test_structure_run_id"
        spans = [MagicMock()]
        exporter = GriptapeCloudSpanExporter()
        result = exporter.export(spans)
        assert result == mock_otlp_span_exporter.export.return_value
        mock_otlp_span_exporter.export.assert_called_once_with(spans)

    def test_shutdown(self, mock_otlp_span_exporter):
        os.environ["GT_CLOUD_STRUCTURE_RUN_ID"] = "test_structure_run_id"
        exporter = GriptapeCloudSpanExporter()
        exporter.shutdown()
        mock_otlp_span_exporter.shutdown.assert_called_once()
