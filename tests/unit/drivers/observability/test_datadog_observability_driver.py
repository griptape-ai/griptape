import os
from unittest.mock import MagicMock

import pytest
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from griptape.drivers import DatadogObservabilityDriver


class TestDatadogTelemetryObservabilityDriver:
    @pytest.fixture()
    def mock_span_exporter(self):
        return MagicMock()

    @pytest.fixture()
    def span_processor(self, mock_span_exporter):
        return BatchSpanProcessor(mock_span_exporter)

    @pytest.fixture()
    def driver(self, span_processor):
        return DatadogObservabilityDriver(span_processor=span_processor)

    def test_init(self):
        driver = DatadogObservabilityDriver()

        assert driver.service_name == "griptape"
        assert driver.datadog_agent_endpoint == "http://localhost:4318/v1/traces"

    def test_init_env_var_dd_agent(self):
        os.environ["DD_AGENT_ENDPOINT"] = "http://griptape.ai:1234/v1/traces"
        driver = DatadogObservabilityDriver()

        assert driver.datadog_agent_endpoint == "http://griptape.ai:1234/v1/traces"

    def test_init_set_dd_agent(self):
        driver = DatadogObservabilityDriver(datadog_agent_endpoint="http://griptape.ai:4321/v1/traces")

        assert driver.datadog_agent_endpoint == "http://griptape.ai:4321/v1/traces"

    def test_init_set_service_name(self):
        driver = DatadogObservabilityDriver(service_name="test")

        assert driver.service_name == "test"
