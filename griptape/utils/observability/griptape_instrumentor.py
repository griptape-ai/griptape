from typing_extensions import override
import wrapt

from collections.abc import Collection
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.instrumentation.utils import unwrap


class GriptapeInstrumentor(BaseInstrumentor):
    @override
    def instrumentation_dependencies(self) -> Collection[str]:
        return []

    @override
    def _instrument(self, **kwargs):
        tracing_provider = kwargs.get("tracer_provider")
        tracer = trace.get_tracer("griptape", None, tracing_provider, None)

        def observable_wrapper_impl(wrapped, instance, args, kwargs, observable_args, observable_kwargs):
            class_name = f"{instance.__class__.__name__}." if instance else ""
            span_name = f"{class_name}{wrapped.__name__}()"
            with tracer.start_as_current_span(span_name) as span:  # pyright: ignore
                try:
                    result = wrapped(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR))
                    span.record_exception(e)
                    raise e

        def observable_wrapper_impl_patch(wrapped, instance, args, kwargs):
            return observable_wrapper_impl(*args[0], *args[1])

        wrapt.wrap_function_wrapper(
            "griptape.utils.decorators", "observable_wrapper_impl", observable_wrapper_impl_patch
        )

    @override
    def _uninstrument(self, **kwargs):
        unwrap_function_wrapper("griptape.utils.decorators", "observable_wrapper_impl")


def unwrap_function_wrapper(module, name):
    (parent, attribute, original) = wrapt.patches.resolve_path(module, name)
    unwrap(parent, attribute)
