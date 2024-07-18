import os
from unittest import mock

from griptape.drivers import DatadogObservabilityDriver


class TestDatadogTelemetryObservabilityDriver:
    def test_init(self):
        driver = DatadogObservabilityDriver()

        assert driver.service_name == "griptape"
        assert driver.datadog_agent_endpoint == "http://localhost:4318"

    @mock.patch.dict(os.environ, {"DD_AGENT_ENDPOINT": "http://griptape.ai:1234"})
    def test_init_env_var_dd_agent(self):
        driver = DatadogObservabilityDriver()

        assert driver.datadog_agent_endpoint == "http://griptape.ai:1234"

    def test_init_set_dd_agent(self):
        driver = DatadogObservabilityDriver(datadog_agent_endpoint="http://griptape.ai:4321")

        assert driver.datadog_agent_endpoint == "http://griptape.ai:4321"

    def test_init_set_service_name(self):
        driver = DatadogObservabilityDriver(service_name="test")

        assert driver.service_name == "test"
