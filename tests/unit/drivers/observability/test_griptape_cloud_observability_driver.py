import os
from uuid import UUID

import pytest
from opentelemetry.sdk.trace import Event, ReadableSpan
from opentelemetry.trace import SpanContext, Status, StatusCode

from griptape.common import Observable
from griptape.drivers import GriptapeCloudObservabilityDriver
from tests.utils.expected_spans import ExpectedSpan, ExpectedSpans


class TestGriptapeCloudObservabilityDriver:
    @pytest.fixture()
    def driver(self):
        environ = {
            "GT_CLOUD_BASE_URL": "http://base-url:1234",
            "GT_CLOUD_API_KEY": "api-key",
            "GT_CLOUD_STRUCTURE_RUN_ID": "structure-run-id",
        }
        original_environ = {}
        for key in environ:
            original_environ[key] = environ.get(key)
            os.environ[key] = environ[key]

        yield GriptapeCloudObservabilityDriver()

        for key, value in original_environ.items():
            if value is None:
                del os.environ[key]
            else:
                os.environ[key] = value

    @pytest.fixture(autouse=True)
    def mock_span_exporter_class(self, mocker):
        return mocker.patch(
            "griptape.drivers.observability.griptape_cloud_observability_driver.GriptapeCloudObservabilityDriver.build_span_exporter"
        )

    @pytest.fixture()
    def mock_span_exporter(self, mock_span_exporter_class):
        return mock_span_exporter_class.return_value

    def test_init(self, mock_span_exporter_class, mock_span_exporter):
        GriptapeCloudObservabilityDriver(
            base_url="http://base-url:1234", api_key="api-key", structure_run_id="structure-run-id"
        )

        assert mock_span_exporter_class.call_count == 1
        mock_span_exporter_class.assert_called_once_with(
            base_url="http://base-url:1234",
            api_key="api-key",
            headers={"Authorization": "Bearer api-key"},
            structure_run_id="structure-run-id",
        )

        mock_span_exporter.export.assert_not_called()

    def test_init_raises_when_structure_run_is_none(self):
        with pytest.raises(ValueError, match="structure_run_id must be set"):
            GriptapeCloudObservabilityDriver(structure_run_id=None)

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

    def test_observe_exception(self, driver, mock_span_exporter):
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

    def test_get_span_id(self, driver):
        assert driver.get_span_id() is None
        with driver:
            # Span ID's returned from GriptapeCloudObservabilityDriver should be valid UUIDs
            assert self._is_valid_uuid(driver.get_span_id())

    def _is_valid_uuid(self, val: str) -> bool:
        try:
            UUID(str(val))
            return True
        except ValueError:
            return False


class TestGriptapeCloudObservabilityDriverSpanExporter:
    @pytest.fixture()
    def mock_post(self, mocker):
        return mocker.patch("requests.post")

    def test_span_exporter_export(self, mock_post):
        exporter = GriptapeCloudObservabilityDriver.build_span_exporter(
            base_url="http://base-url:1234",
            api_key="api-key",
            headers={"Authorization": "Bearer api-key"},
            structure_run_id="structure-run-id",
        )

        exporter.export(
            [
                ReadableSpan(
                    name="main",
                    parent=None,
                    context=SpanContext(trace_id=1, span_id=2, is_remote=False),
                    start_time=3000,
                    end_time=4000,
                    attributes={"key": "value"},
                ),
                ReadableSpan(
                    name="thing-1",
                    parent=SpanContext(trace_id=1, span_id=2, is_remote=False),
                    context=SpanContext(trace_id=1, span_id=3, is_remote=False),
                    start_time=8000,
                    end_time=9000,
                    status=Status(status_code=StatusCode.OK),
                ),
                ReadableSpan(
                    name="thing-2",
                    parent=SpanContext(trace_id=1, span_id=2, is_remote=False),
                    context=SpanContext(trace_id=1, span_id=3, is_remote=False),
                    start_time=8000,
                    end_time=9000,
                    status=Status(status_code=StatusCode.ERROR),
                    events=[
                        Event(
                            timestamp=10000,
                            name="exception",
                            attributes={
                                "exception.type": "Exception",
                                "exception.message": "Boom",
                                "exception.stacktrace": "Traceback (most recent call last) ...",
                            },
                        )
                    ],
                ),
            ]
        )

        mock_post.assert_called_once_with(
            url="http://base-url:1234/api/structure-runs/structure-run-id/spans",
            json=[
                {
                    "trace_id": "00000000-0000-0000-0000-000000000001",
                    "span_id": "00000000-0000-0000-0000-000000000002",
                    "parent_id": None,
                    "name": "main",
                    "start_time": "1970-01-01T00:00:00.000003Z",
                    "end_time": "1970-01-01T00:00:00.000004Z",
                    "status": "UNSET",
                    "attributes": {"key": "value"},
                    "events": [],
                },
                {
                    "trace_id": "00000000-0000-0000-0000-000000000001",
                    "span_id": "00000000-0000-0000-0000-000000000003",
                    "parent_id": "00000000-0000-0000-0000-000000000002",
                    "name": "thing-1",
                    "start_time": "1970-01-01T00:00:00.000008Z",
                    "end_time": "1970-01-01T00:00:00.000009Z",
                    "status": "OK",
                    "attributes": {},
                    "events": [],
                },
                {
                    "trace_id": "00000000-0000-0000-0000-000000000001",
                    "span_id": "00000000-0000-0000-0000-000000000003",
                    "parent_id": "00000000-0000-0000-0000-000000000002",
                    "name": "thing-2",
                    "start_time": "1970-01-01T00:00:00.000008Z",
                    "end_time": "1970-01-01T00:00:00.000009Z",
                    "status": "ERROR",
                    "attributes": {},
                    "events": [
                        {
                            "timestamp": "1970-01-01T00:00:00.000010Z",
                            "name": "exception",
                            "attributes": {
                                "exception.type": "Exception",
                                "exception.message": "Boom",
                                "exception.stacktrace": "Traceback (most recent call last) ...",
                            },
                        }
                    ],
                },
            ],
            headers={"Authorization": "Bearer api-key"},
        )
