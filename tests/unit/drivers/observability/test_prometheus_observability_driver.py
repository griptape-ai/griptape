from __future__ import annotations

from itertools import groupby
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from prometheus_client import CollectorRegistry, generate_latest

from griptape.common.observable import Observable
from griptape.drivers.observability.prometheus_observability_driver import PrometheusObservabilityDriver


def validate_call_count(driver):
    # Assuming collected_metrics is obtained from driver.request_count.collect()
    collected_metrics = list(driver.request_count.collect())

    # Group samples by name and method
    grouped_samples = groupby(sorted(collected_metrics[0].samples, key=lambda s: (s.name, s.labels['method'])), key=lambda s: (s.name, s.labels['method']))

    # Assert that each group has a count of 1
    for (name, method), group in grouped_samples:
        sample_count = len(list(group))  # Count the number of samples in this group
        assert sample_count == 1, f"Expected 1 sample for {name} with method {method}, but got {sample_count}"

class TestPrometheusObservabilityDriver:
    @pytest.fixture()
    def driver(self):
        # Mock the span processor for Prometheus driver
        mock_span_processor = MagicMock()
        def get_driver(service_name):
            # generate singleton around the tests service name to avoid name clash
            return PrometheusObservabilityDriver(
                service_name=service_name,
                span_processor=mock_span_processor
            )
        return get_driver

    @pytest.fixture()
    def metrics(self):
        # Create a fresh registry for each test
        return CollectorRegistry()



    def test_observe(self, driver, metrics):
        driver = driver('test_observe')
        # Register metrics to the custom registry
        metrics.register(driver.request_count)
        metrics.register(driver.request_duration)

        def foo_append(word: str):
            return word + " foo"

        class TestKlass:
            def bazqux_append(self, word: str):
                return word + " bazqux"

        instance = TestKlass()

        with driver:
            assert driver.observe(Observable.Call(func=foo_append, instance=None, args=["hello"])) == "hello foo"
            assert driver.observe(Observable.Call(func=instance.bazqux_append, instance=instance, args=["WORLD"])) == "WORLD bazqux"
        validate_call_count(driver)

    def test_metrics_exposure(self, driver, metrics):
        driver = driver('test_metrics_exposure')

        # Test if the metrics can be exposed
        metrics.register(driver.request_count)
        metrics.register(driver.request_duration)

        def foo_append(word: str):
            return word + " foo"

        with driver:
            driver.observe(Observable.Call(func=foo_append, instance=None, args=["hello"]))

        # Generate metrics
        metric_output = generate_latest(metrics)

        # Check that the metrics output contains the expected information
        assert b'test_metrics_exposure_request_count' in metric_output
        assert b'test_metrics_exposure_request_duration_seconds' in metric_output

    def test_get_span_id(self, driver):
        driver = driver('test_get_span_id')
        assert driver.get_span_id() is None
        with driver:
            span_id = driver.get_span_id()
            assert span_id is not None
            assert isinstance(span_id, str)

    def test_context_manager_observe(self, driver, metrics):
        driver = driver('test_context_manager_observe')
        metrics.register(driver.request_count)
        metrics.register(driver.request_duration)

        def qux_append(word: str):
            return word + " qux"

        class TestKlass:
            def quux_append(self, word: str):
                return word + " quux"

        instance = TestKlass()

        with driver:
            assert driver.observe(Observable.Call(func=qux_append, instance=None, args=["Greetings"])) == "Greetings qux"
            assert driver.observe(Observable.Call(func=instance.quux_append, instance=instance, args=["Farewell"])) == "Farewell quux"

        validate_call_count(driver)

    def test_context_manager_observe_exception(self, driver, metrics):
        driver = driver('test_context_manager_observe_exception')
        metrics.register(driver.request_count)
        metrics.register(driver.request_duration)

        def func(word: str):
            raise Exception("Error in function")

        with pytest.raises(Exception, match="Error in function"), driver:
            driver.observe(Observable.Call(func=func, instance=None, args=["test"]))

        # Ensure metrics are still updated despite the exception
        validate_call_count(driver)
