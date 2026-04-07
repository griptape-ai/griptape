from __future__ import annotations

import pytest

from griptape.common.observable import Observable
from griptape.drivers.observability.no_op_observability_driver import NoOpObservabilityDriver


class TestNoOpObservabilityDriver:
    @pytest.fixture()
    def driver(self):
        return NoOpObservabilityDriver()

    def test_observe(self, driver):
        def func(word: str):
            return word + " you"

        class Klass:
            def method(self, word: str):
                return word + " yous"

        instance = Klass()

        with driver:
            assert driver.observe(Observable.Call(func=func, instance=None, args=["Hi"])) == "Hi you"
            assert driver.observe(Observable.Call(func=instance.method, instance=instance, args=["Bye"])) == "Bye yous"

    def test_get_span_id(self, driver):
        assert driver.get_span_id() is None

        with driver:
            assert driver.get_span_id() is None
