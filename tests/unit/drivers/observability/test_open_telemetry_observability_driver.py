from unittest.mock import MagicMock
import pytest
from griptape.drivers.observability.open_telemetry_observability_driver import OpenTelemetryObservabilityDriver
from opentelemetry.trace import StatusCode
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from griptape.observability.observability import Observability
from griptape.structures.agent import Agent
from tests.mocks.mock_prompt_driver import MockPromptDriver
from tests.utils.expected_spans import ExpectedSpan, ExpectedSpans


class TestOpenTelemetryObservabilityDriver:
    @pytest.fixture
    def mock_span_exporter(self):
        return MagicMock()

    @pytest.fixture
    def span_processor(self, mock_span_exporter):
        return BatchSpanProcessor(mock_span_exporter)

    @pytest.fixture
    def driver(self, span_processor):
        return OpenTelemetryObservabilityDriver(service_name="test", span_processor=span_processor)

    def test_init(self, span_processor):
        OpenTelemetryObservabilityDriver(service_name="test", span_processor=span_processor)

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

        with pytest.raises(Exception, match="Boom"):
            with driver:
                raise Exception("Boom")

        assert mock_span_exporter.export.call_count == 1
        mock_span_exporter.export.assert_called_with(expected_spans)
        mock_span_exporter.export.reset_mock()

        # Works second time too
        with pytest.raises(Exception, match="Boom"):
            with driver:
                raise Exception("Boom")

        assert mock_span_exporter.export.call_count == 1
        mock_span_exporter.export.assert_called_with(expected_spans)
        mock_span_exporter.export.reset_mock()

    def test_context_manager_invoke_observable(self, driver, mock_span_exporter):
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
            driver.invoke_observable(func, None, ["Hi"], {}, {}, {}) == "Hi you"
            driver.invoke_observable(instance.method, instance, ["Bye"], {}, {}, {}) == "Bye yous"

        assert mock_span_exporter.export.call_count == 1
        mock_span_exporter.export.assert_called_with(expected_spans)
        mock_span_exporter.export.reset_mock()

        # Works second time too
        with driver:
            driver.invoke_observable(func, None, ["Hi"], {}, {}, {}) == "Hi you"
            driver.invoke_observable(instance.method, instance, ["Bye"], {}, {}, {}) == "Bye yous"

        assert mock_span_exporter.export.call_count == 1
        mock_span_exporter.export.assert_called_with(expected_spans)
        mock_span_exporter.export.reset_mock()

    def test_context_manager_invoke_observable_exception_function(self, driver, mock_span_exporter):
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

        with pytest.raises(Exception, match="Boom func"):
            with driver:
                driver.invoke_observable(func, None, ["Hi"], {}, {}, {}) == "Hi you"

        assert mock_span_exporter.export.call_count == 1
        mock_span_exporter.export.assert_called_with(expected_spans)

    def test_context_manager_invoke_observable_exception_method(self, driver, mock_span_exporter):
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
        with pytest.raises(Exception, match="Boom meth"):
            with driver:
                driver.invoke_observable(instance.method, instance, ["Bye"], {}, {}, {}) == "Bye yous"

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
                ExpectedSpan(name="Agent.after_run()", parent="Agent.run()", status_code=StatusCode.OK),
            ]
        )

        with Observability(driver=driver):
            agent = Agent(prompt_driver=MockPromptDriver())
            agent.run("Hi")

        assert mock_span_exporter.export.call_count == 1
        mock_span_exporter.export.assert_called_with(expected_spans)
        mock_span_exporter.export.reset_mock()
