from __future__ import annotations

from time import perf_counter
from typing import TYPE_CHECKING, Any

from attrs import Factory, define, field

from griptape.drivers.observability import BaseObservabilityDriver
from griptape.utils.import_utils import import_optional_dependency

if TYPE_CHECKING:
    from types import TracebackType

    from opentelemetry.metrics import Counter, Histogram
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.trace import SpanProcessor, TracerProvider
    from opentelemetry.trace import Tracer

    from griptape.common import Observable
    from griptape.drivers.prompt import BasePromptDriver


_PROMPT_DRIVER_PROVIDERS = {
    "AmazonBedrockPromptDriver": ("aws.bedrock", "chat"),
    "AmazonSageMakerJumpstartPromptDriver": ("aws.sagemaker", "text_completion"),
    "AnthropicPromptDriver": ("anthropic", "chat"),
    "AzureOpenAiChatPromptDriver": ("azure.ai.openai", "chat"),
    "CoherePromptDriver": ("cohere", "chat"),
    "GooglePromptDriver": ("gcp.gen_ai", "generate_content"),
    "GriptapeCloudPromptDriver": ("griptape", "chat"),
    "GrokPromptDriver": ("x_ai", "chat"),
    "HuggingFaceHubPromptDriver": ("huggingface", "text_completion"),
    "HuggingFacePipelinePromptDriver": ("huggingface", "text_completion"),
    "OllamaPromptDriver": ("ollama", "chat"),
    "OpenAiChatPromptDriver": ("openai", "chat"),
    "PerplexityPromptDriver": ("perplexity", "chat"),
}


@define
class OpenTelemetryObservabilityDriver(BaseObservabilityDriver):
    service_name: str = field(default="griptape", kw_only=True)
    span_processor: SpanProcessor = field(kw_only=True)
    service_version: str | None = field(default=None, kw_only=True)
    deployment_env: str | None = field(default=None, kw_only=True)
    meter_provider: MeterProvider | None = field(default=None, kw_only=True)
    trace_provider: TracerProvider = field(
        default=Factory(
            lambda self: self._trace_provider_factory(),
            takes_self=True,
        ),
        kw_only=True,
    )
    _tracer: Tracer = field(init=False)
    _operation_duration: Histogram = field(init=False)
    _input_token_usage: Counter = field(init=False)
    _output_token_usage: Counter = field(init=False)
    _input_tokens: Histogram = field(init=False)
    _output_tokens: Histogram = field(init=False)
    _root_span_context_manager: Any = None

    def _trace_provider_factory(self) -> TracerProvider:
        opentelemetry_trace = import_optional_dependency("opentelemetry.sdk.trace")

        attributes = {"service.name": self.service_name}
        if self.service_version is not None:
            attributes["service.version"] = self.service_version
        if self.deployment_env is not None:
            attributes["deployment.environment"] = self.deployment_env
        return opentelemetry_trace.TracerProvider(
            resource=import_optional_dependency("opentelemetry.sdk.resources").Resource(attributes=attributes)
        )  # pyright: ignore[reportArgumentType]

    def __attrs_post_init__(self) -> None:
        opentelemetry_trace = import_optional_dependency("opentelemetry.trace")
        self.trace_provider.add_span_processor(self.span_processor)
        self._tracer = opentelemetry_trace.get_tracer(self.service_name, tracer_provider=self.trace_provider)
        meter = import_optional_dependency("opentelemetry.metrics").get_meter(
            self.service_name, meter_provider=self.meter_provider
        )
        self._operation_duration = meter.create_histogram(
            "gen_ai.client.operation.duration", unit="s", description="GenAI operation duration."
        )
        self._input_token_usage = meter.create_counter(
            "gen_ai.client.inference.usage.input_tokens", unit="{token}", description="Number of input tokens used."
        )
        self._output_token_usage = meter.create_counter(
            "gen_ai.client.inference.usage.output_tokens", unit="{token}", description="Number of output tokens used."
        )
        self._input_tokens = meter.create_histogram(
            "gen_ai.client.inference.operation.input_tokens", unit="{token}", description="Input tokens per operation."
        )
        self._output_tokens = meter.create_histogram(
            "gen_ai.client.inference.operation.output_tokens",
            unit="{token}",
            description="Output tokens per operation.",
        )

    def __enter__(self) -> None:
        opentelemetry_instrumentation_threading = import_optional_dependency("opentelemetry.instrumentation.threading")

        opentelemetry_instrumentation_threading.ThreadingInstrumentor().instrument()
        self._root_span_context_manager = self._tracer.start_as_current_span("main")  # pyright: ignore[reportCallIssue]
        self._root_span_context_manager.__enter__()

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        exc_traceback: TracebackType | None,
    ) -> bool:
        opentelemetry_trace = import_optional_dependency("opentelemetry.trace")
        opentelemetry_instrumentation_threading = import_optional_dependency("opentelemetry.instrumentation.threading")
        root_span = opentelemetry_trace.get_current_span()
        if exc_value:
            root_span = opentelemetry_trace.get_current_span()
            root_span.set_status(opentelemetry_trace.Status(opentelemetry_trace.StatusCode.ERROR))
            root_span.record_exception(exc_value)
        else:
            root_span.set_status(opentelemetry_trace.Status(opentelemetry_trace.StatusCode.OK))
        if self._root_span_context_manager:
            self._root_span_context_manager.__exit__(exc_type, exc_value, exc_traceback)
            self._root_span_context_manager = None
        self.trace_provider.force_flush()
        if self.meter_provider is not None:
            self.meter_provider.force_flush()
        opentelemetry_instrumentation_threading.ThreadingInstrumentor().uninstrument()
        return False

    def observe(self, call: Observable.Call) -> Any:
        from griptape.common import Message
        from griptape.drivers.prompt import BasePromptDriver

        open_telemetry_trace = import_optional_dependency("opentelemetry.trace")
        func = call.func
        instance = call.instance
        tags = call.tags
        attributes = (
            self._prompt_driver_attributes(instance)
            if isinstance(instance, BasePromptDriver) and func.__name__ == "run"
            else None
        )

        class_name = f"{instance.__class__.__name__}." if instance else ""
        span_name = f"{class_name}{func.__name__}()"
        with self._tracer.start_as_current_span(span_name) as span:  # pyright: ignore[reportCallIssue]
            if tags is not None:
                span.set_attribute("tags", tags)

            start_time = perf_counter() if attributes is not None else None
            try:
                result = call()
                if attributes is not None and isinstance(result, Message):
                    self._record_token_usage(result.usage.input_tokens, result.usage.output_tokens, attributes)
                span.set_status(open_telemetry_trace.Status(open_telemetry_trace.StatusCode.OK))
                return result
            except Exception as e:
                span.set_status(open_telemetry_trace.Status(open_telemetry_trace.StatusCode.ERROR))
                span.record_exception(e)
                if attributes is not None:
                    attributes["error.type"] = f"{type(e).__module__}.{type(e).__qualname__}"
                raise e
            finally:
                if start_time is not None:
                    self._operation_duration.record(perf_counter() - start_time, attributes=attributes)

    @staticmethod
    def _prompt_driver_attributes(driver: BasePromptDriver) -> dict[str, str]:
        # Inspect the MRO so user subclasses retain their provider's conventions.
        provider, operation = next(
            (
                _PROMPT_DRIVER_PROVIDERS[cls.__name__]
                for cls in type(driver).__mro__
                if cls.__name__ in _PROMPT_DRIVER_PROVIDERS
            ),
            (type(driver).__name__, "chat"),
        )
        return {
            "gen_ai.operation.name": operation,
            "gen_ai.provider.name": provider,
            "gen_ai.request.model": driver.model,
        }

    def _record_token_usage(
        self, input_tokens: float | None, output_tokens: float | None, attributes: dict[str, str]
    ) -> None:
        # Griptape reports aggregate usage; do not guess the token modality or
        # manufacture zero counts when a provider does not report usage.
        usage_attributes = {**attributes, "gen_ai.token.modality": "unknown"}
        if input_tokens is not None and input_tokens >= 0:
            self._input_token_usage.add(input_tokens, attributes=usage_attributes)
            self._input_tokens.record(input_tokens, attributes=attributes)
        if output_tokens is not None and output_tokens >= 0:
            self._output_token_usage.add(output_tokens, attributes=usage_attributes)
            self._output_tokens.record(output_tokens, attributes=attributes)

    def get_span_id(self) -> str | None:
        opentelemetry_trace = import_optional_dependency("opentelemetry.trace")
        span = opentelemetry_trace.get_current_span()
        if span is opentelemetry_trace.INVALID_SPAN:
            return None
        return opentelemetry_trace.format_span_id(span.get_span_context().span_id)
