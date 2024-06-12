import pytest
from griptape.drivers.observability.griptape_cloud_observabillity_driver import GriptapeCloudObservabilityDriver
from opentelemetry.trace import StatusCode
from tests.utils.expected_spans import ExpectedSpan, ExpectedSpans


class TestGriptapeCloudObservabilityDriver:
    @pytest.fixture
    def driver(self):
        return GriptapeCloudObservabilityDriver(
            service_name="test", base_url="http://base-url:1234", api_key="api-key", structure_run_id="structure-run-id"
        )

    @pytest.fixture(autouse=True)
    def mock_span_exporter_class(self, mocker):
        return mocker.patch("griptape.drivers.observability.griptape_cloud_observabillity_driver.OTLPSpanExporter")

    @pytest.fixture
    def mock_span_exporter(self, mock_span_exporter_class):
        return mock_span_exporter_class.return_value

    def test_init(self, mock_span_exporter_class, mock_span_exporter):
        GriptapeCloudObservabilityDriver(
            service_name="test", base_url="http://base-url:1234", api_key="api-key", structure_run_id="structure-run-id"
        )

        assert mock_span_exporter_class.call_count == 1
        mock_span_exporter_class.assert_called_once_with(
            endpoint="http://base-url:1234/api/structure-runs/structure-run-id/spans",
            headers={"Authorization": "Bearer api-key"},
        )

        mock_span_exporter.export.assert_not_called()

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

    def test_context_manager_pass_exc(self, driver, mock_span_exporter):
        expected_spans = ExpectedSpans(spans=[ExpectedSpan(name="main", parent=None, status_code=StatusCode.ERROR)])

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

    def test_invoke_observable_exception(self, driver, mock_span_exporter):
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
