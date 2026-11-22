from unittest.mock import MagicMock

import pytest
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import InMemoryMetricReader, Metric
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import StatusCode

from griptape.common import DeltaMessage, Message, Observable, PromptStack, TextDeltaMessageContent
from griptape.drivers.observability.open_telemetry import OpenTelemetryObservabilityDriver
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
            agent = Agent()
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

    @pytest.fixture()
    def metrics(self, span_processor):
        reader = InMemoryMetricReader()
        provider = MeterProvider(metric_readers=[reader])
        driver = OpenTelemetryObservabilityDriver(span_processor=span_processor, meter_provider=provider)
        yield driver, reader
        provider.shutdown()

    @staticmethod
    def collect_metrics(reader) -> dict[str, Metric]:
        data = reader.get_metrics_data()
        if data is None:
            return {}
        return {
            metric.name: metric
            for resource in data.resource_metrics
            for scope in resource.scope_metrics
            for metric in scope.metrics
        }

    @pytest.mark.parametrize("stream", [False, True])
    def test_prompt_metrics(self, metrics, mocker, stream):
        driver, reader = metrics
        mocker.patch(
            "griptape.drivers.observability.open_telemetry_observability_driver.perf_counter",
            side_effect=[10.0, 12.5],
        )
        prompt_driver = MockPromptDriver(stream=stream)
        if stream:
            mocker.patch.object(
                prompt_driver,
                "try_stream",
                return_value=iter(
                    [
                        DeltaMessage(
                            content=TextDeltaMessageContent("Hi"),
                            usage=DeltaMessage.Usage(input_tokens=100, output_tokens=100),
                        )
                    ]
                ),
            )
        with Observability(observability_driver=driver):
            result = prompt_driver.run(PromptStack())

        assert result.usage.input_tokens == 100
        actual = self.collect_metrics(reader)
        assert set(actual) == {
            "gen_ai.client.operation.duration",
            "gen_ai.client.inference.usage.input_tokens",
            "gen_ai.client.inference.usage.output_tokens",
            "gen_ai.client.inference.operation.input_tokens",
            "gen_ai.client.inference.operation.output_tokens",
        }
        attributes = {
            "gen_ai.operation.name": "chat",
            "gen_ai.provider.name": "MockPromptDriver",
            "gen_ai.request.model": "test-model",
        }
        duration = actual["gen_ai.client.operation.duration"]
        assert duration.unit == "s"
        assert len(duration.data.data_points) == 1
        assert duration.data.data_points[0].count == 1
        assert duration.data.data_points[0].sum == 2.5
        assert dict(duration.data.data_points[0].attributes) == attributes
        for token_type in ("input", "output"):
            usage = actual[f"gen_ai.client.inference.usage.{token_type}_tokens"]
            assert usage.unit == "{token}"
            assert usage.data.is_monotonic
            assert usage.data.data_points[0].value == 100
            assert dict(usage.data.data_points[0].attributes) == {**attributes, "gen_ai.token.modality": "unknown"}
            histogram = actual[f"gen_ai.client.inference.operation.{token_type}_tokens"]
            assert histogram.unit == "{token}"
            assert histogram.data.data_points[0].sum == 100
            assert histogram.data.data_points[0].count == 1
            assert dict(histogram.data.data_points[0].attributes) == attributes

    @pytest.mark.parametrize(("input_tokens", "output_tokens"), [(None, None), (0, None), (None, 5), (-1, 5)])
    def test_prompt_metrics_missing_usage(self, metrics, mocker, input_tokens, output_tokens):
        driver, reader = metrics
        result = Message(
            content=[],
            role=Message.ASSISTANT_ROLE,
            usage=Message.Usage(input_tokens=input_tokens, output_tokens=output_tokens),
        )
        prompt_driver = MockPromptDriver()
        mocker.patch.object(prompt_driver, "try_run", return_value=result)
        with Observability(observability_driver=driver):
            assert prompt_driver.run(PromptStack()) is result
        actual = self.collect_metrics(reader)
        for token_type, count in (("input", input_tokens), ("output", output_tokens)):
            name = f"gen_ai.client.inference.usage.{token_type}_tokens"
            if count is None or count < 0:
                assert name not in actual
                assert f"gen_ai.client.inference.operation.{token_type}_tokens" not in actual
            else:
                assert actual[name].data.data_points[0].value == count

    @pytest.mark.parametrize("stream", [False, True])
    def test_prompt_metrics_error(self, metrics, mocker, stream):
        driver, reader = metrics
        prompt_driver = MockPromptDriver(stream=stream, max_attempts=1)
        error = ValueError("private prompt content")
        mocker.patch.object(prompt_driver, "try_stream" if stream else "try_run", side_effect=error)
        with Observability(observability_driver=driver), pytest.raises(ValueError) as exc:
            prompt_driver.run(PromptStack())
        assert exc.value is error
        actual = self.collect_metrics(reader)
        assert set(actual) == {"gen_ai.client.operation.duration"}
        point = actual["gen_ai.client.operation.duration"].data.data_points[0]
        assert point.count == 1
        assert point.attributes["error.type"] == "builtins.ValueError"
        assert "private prompt content" not in str(point.attributes)

    def test_prompt_metrics_retries(self, metrics, mocker):
        driver, reader = metrics
        prompt_driver = MockPromptDriver(max_attempts=2, min_retry_delay=0, max_retry_delay=0)
        result = prompt_driver.try_run(PromptStack())
        attempt = mocker.patch.object(prompt_driver, "try_run", side_effect=[RuntimeError("retry"), result])
        with Observability(observability_driver=driver):
            assert prompt_driver.run(PromptStack()) is result
        assert attempt.call_count == 2
        actual = self.collect_metrics(reader)
        point = actual["gen_ai.client.operation.duration"].data.data_points[0]
        assert point.count == 1
        assert "error.type" not in point.attributes
        assert actual["gen_ai.client.inference.usage.input_tokens"].data.data_points[0].value == 100

    def test_stream_metrics_use_final_usage(self, metrics, mocker):
        driver, reader = metrics
        prompt_driver = MockPromptDriver(stream=True)
        mocker.patch.object(
            prompt_driver,
            "try_stream",
            return_value=iter(
                [
                    DeltaMessage(
                        content=TextDeltaMessageContent("Hi"),
                        usage=DeltaMessage.Usage(input_tokens=20, output_tokens=1),
                    ),
                    DeltaMessage(usage=DeltaMessage.Usage(output_tokens=4)),
                    DeltaMessage(usage=DeltaMessage.Usage(output_tokens=7)),
                ]
            ),
        )
        with Observability(observability_driver=driver):
            prompt_driver.run(PromptStack())
        actual = self.collect_metrics(reader)
        assert actual["gen_ai.client.inference.usage.input_tokens"].data.data_points[0].value == 20
        assert actual["gen_ai.client.inference.usage.output_tokens"].data.data_points[0].value == 7

    def test_non_prompt_calls_do_not_emit_metrics(self, metrics):
        driver, reader = metrics
        with driver:
            assert driver.observe(Observable.Call(func=lambda: "result")) == "result"
        assert self.collect_metrics(reader) == {}

    def test_prompt_provider_subclass(self, metrics, mocker):
        from griptape.drivers.prompt.azure_openai_chat_prompt_driver import AzureOpenAiChatPromptDriver
        from tests.mocks.mock_tokenizer import MockTokenizer

        class CustomAzureDriver(AzureOpenAiChatPromptDriver):
            pass

        driver, reader = metrics
        prompt_driver = CustomAzureDriver(
            model="deployment-name",
            tokenizer=MockTokenizer(model="deployment-name"),
            azure_endpoint="https://example.com",
        )
        mocker.patch.object(prompt_driver, "try_run", return_value=Message(content=[], role=Message.ASSISTANT_ROLE))
        with Observability(observability_driver=driver):
            prompt_driver.run(PromptStack())
        point = self.collect_metrics(reader)["gen_ai.client.operation.duration"].data.data_points[0]
        assert point.attributes["gen_ai.provider.name"] == "azure.ai.openai"
        assert point.attributes["gen_ai.request.model"] == "deployment-name"

    def test_meter_provider_flush_and_reuse(self, metrics, mocker):
        driver, reader = metrics
        flush = mocker.spy(driver.meter_provider, "force_flush")
        for _ in range(2):
            with Observability(observability_driver=driver):
                MockPromptDriver().run(PromptStack())
        assert flush.call_count == 2
        point = self.collect_metrics(reader)["gen_ai.client.operation.duration"].data.data_points[0]
        assert point.count == 2

    def test_global_meter_provider(self, span_processor, mocker):
        reader = InMemoryMetricReader()
        provider = MeterProvider(metric_readers=[reader])
        mocker.patch("opentelemetry.metrics._internal._METER_PROVIDER", provider)
        driver = OpenTelemetryObservabilityDriver(span_processor=span_processor)
        try:
            with Observability(observability_driver=driver):
                MockPromptDriver().run(PromptStack())
            assert "gen_ai.client.operation.duration" in self.collect_metrics(reader)
        finally:
            provider.shutdown()
