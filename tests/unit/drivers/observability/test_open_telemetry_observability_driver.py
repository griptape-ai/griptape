from unittest.mock import MagicMock

import pytest
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import StatusCode

from griptape.common import Observable
from griptape.drivers import OpenTelemetryObservabilityDriver
from griptape.observability.observability import Observability
from griptape.structures.agent import Agent
from tests.mocks.mock_prompt_driver import MockPromptDriver
from tests.utils.expected_spans import ExpectedSpan, ExpectedSpans


class TestOpenTelemetryObservabilityDriver:
    @pytest.fixture()
    def mock_span_exporter(self):
        return MagicMock()

    @pytest.fixture()
    def span_processor(self, mock_span_exporter):
        return BatchSpanProcessor(mock_span_exporter)

    @pytest.fixture()
    def driver(self, span_processor):
        return OpenTelemetryObservabilityDriver(span_processor=span_processor)

    def test_init_no_optional(self, span_processor):
        driver = OpenTelemetryObservabilityDriver(span_processor=span_processor)

        assert driver.service_name == "griptape"
        assert driver.service_version is None
        assert driver.deployment_env is None

    def test_init_all_optional(self, span_processor):
        driver = OpenTelemetryObservabilityDriver(
            service_name="griptape", service_version="1.0", deployment_env="test", span_processor=span_processor
        )

        assert driver.service_name == "griptape"
        assert driver.service_version == "1.0"
        assert driver.deployment_env == "test"

    def test_context_manager_pass(self, driver, mock_span_exporter):
        expected_spans = ExpectedSpans(spans=[ExpectedSpan(name="main", parent=None, status_code=StatusCode.OK)])

        with driver:
            pass

        assert mock_span_exporter.export.call_count == 1
        mock_span_exporter.export.assert_called_with(expected_spans)
        mock_span_exporter.export.reset_mock()

        # Works second time too
        with driver:
            pass

        assert mock_span_exporter.export.call_count == 1
        mock_span_exporter.export.assert_called_with(expected_spans)
        mock_span_exporter.export.reset_mock()

    def test_context_manager_exception(self, driver, mock_span_exporter):
        expected_spans = ExpectedSpans(
            spans=[ExpectedSpan(name="main", parent=None, status_code=StatusCode.ERROR, exception=Exception("Boom"))]
        )

        with pytest.raises(Exception, match="Boom"), driver:
            raise Exception("Boom")

        assert mock_span_exporter.export.call_count == 1
        mock_span_exporter.export.assert_called_with(expected_spans)
        mock_span_exporter.export.reset_mock()

        # Works second time too
        with pytest.raises(Exception, match="Boom"), driver:
            raise Exception("Boom")

        assert mock_span_exporter.export.call_count == 1
        mock_span_exporter.export.assert_called_with(expected_spans)
        mock_span_exporter.export.reset_mock()

    def test_context_manager_observe(self, driver, mock_span_exporter):
        expected_spans = ExpectedSpans(
            spans=[
                ExpectedSpan(name="main", parent=None, status_code=StatusCode.OK),
                ExpectedSpan(name="func()", parent="main", status_code=StatusCode.OK),
                ExpectedSpan(name="Klass.method()", parent="main", status_code=StatusCode.OK),
            ]
        )

        def func(word: str):
            return word + " you"

        class Klass:
            def method(self, word: str):
                return word + " yous"

        instance = Klass()

        with driver:
            assert driver.observe(Observable.Call(func=func, instance=None, args=["Hi"])) == "Hi you"
            assert driver.observe(Observable.Call(func=instance.method, instance=instance, args=["Bye"])) == "Bye yous"

        assert mock_span_exporter.export.call_count == 1
        mock_span_exporter.export.assert_called_with(expected_spans)
        mock_span_exporter.export.reset_mock()

        # Works second time too
        with driver:
            assert driver.observe(Observable.Call(func=func, instance=None, args=["Hi"])) == "Hi you"
            assert driver.observe(Observable.Call(func=instance.method, instance=instance, args=["Bye"])) == "Bye yous"

        assert mock_span_exporter.export.call_count == 1
        mock_span_exporter.export.assert_called_with(expected_spans)
        mock_span_exporter.export.reset_mock()

    def test_context_manager_observe_exception_function(self, driver, mock_span_exporter):
        expected_spans = ExpectedSpans(
            spans=[
                ExpectedSpan(name="main", parent=None, status_code=StatusCode.ERROR, exception=Exception("Boom func")),
                ExpectedSpan(
                    name="func()", parent="main", status_code=StatusCode.ERROR, exception=Exception("Boom func")
                ),
            ]
        )

        def func(word: str):
            raise Exception("Boom func")

        with pytest.raises(Exception, match="Boom func"), driver:
            assert driver.observe(Observable.Call(func=func, instance=None, args=["Hi"])) == "Hi you"

        assert mock_span_exporter.export.call_count == 1
        mock_span_exporter.export.assert_called_with(expected_spans)

    def test_context_manager_observe_exception_method(self, driver, mock_span_exporter):
        expected_spans = ExpectedSpans(
            spans=[
                ExpectedSpan(name="main", parent=None, status_code=StatusCode.ERROR, exception=Exception("Boom meth")),
                ExpectedSpan(
                    name="Klass.method()", parent="main", status_code=StatusCode.ERROR, exception=Exception("Boom meth")
                ),
            ]
        )

        class Klass:
            def method(self, word: str):
                raise Exception("Boom meth")

        instance = Klass()

        # Works second time too
        with pytest.raises(Exception, match="Boom meth"), driver:
            assert driver.observe(Observable.Call(func=instance.method, instance=instance, args=["Bye"])) == "Bye yous"

        assert mock_span_exporter.export.call_count == 1
        mock_span_exporter.export.assert_called_with(expected_spans)
        mock_span_exporter.export.reset_mock()

    def test_observability_agent(self, driver, mock_span_exporter):
        expected_spans = ExpectedSpans(
            spans=[
                ExpectedSpan(name="main", parent=None, status_code=StatusCode.OK),
                ExpectedSpan(name="Agent.run()", parent="main", status_code=StatusCode.OK),
                ExpectedSpan(name="Agent.before_run()", parent="Agent.run()", status_code=StatusCode.OK),
                ExpectedSpan(name="Agent.try_run()", parent="Agent.run()", status_code=StatusCode.OK),
                ExpectedSpan(name="MockPromptDriver.run()", parent="Agent.try_run()", status_code=StatusCode.OK),
                ExpectedSpan(name="Agent.after_run()", parent="Agent.run()", status_code=StatusCode.OK),
            ]
        )

        with Observability(observability_driver=driver):
            agent = Agent(prompt_driver=MockPromptDriver())
            agent.run("Hi")

        assert mock_span_exporter.export.call_count == 1
        mock_span_exporter.export.assert_called_with(expected_spans)
        mock_span_exporter.export.reset_mock()

    def test_context_manager_observe_adds_tags_attribute(self, driver, mock_span_exporter):
        expected_spans = ExpectedSpans(
            spans=[
                ExpectedSpan(name="main", parent=None, status_code=StatusCode.OK),
                ExpectedSpan(
                    name="func()", parent="main", status_code=StatusCode.OK, attributes={"tags": ("Foo.bar()",)}
                ),
            ]
        )

        def func(word: str):
            return word + " you"

        with driver:
            assert (
                driver.observe(
                    Observable.Call(func=func, instance=None, args=["Hi"], decorator_kwargs={"tags": ["Foo.bar()"]})
                )
                == "Hi you"
            )

        assert mock_span_exporter.export.call_count == 1
        mock_span_exporter.export.assert_called_with(expected_spans)
        mock_span_exporter.export.reset_mock()

    def test_get_span_id(self, driver):
        assert driver.get_span_id() is None
        with driver:
            span_id = driver.get_span_id()
            assert span_id is not None
            assert isinstance(span_id, str)
