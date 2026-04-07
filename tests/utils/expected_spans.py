from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from attrs import define, field
from opentelemetry.trace import SpanKind, StatusCode

if TYPE_CHECKING:
    from collections.abc import Sequence

    from opentelemetry.sdk.trace import ReadableSpan


@define
class ExpectedSpan:
    name: str = field(kw_only=True)
    parent: str = field(kw_only=True)
    status_code: StatusCode = field(kw_only=True)
    exception: Optional[Exception] = field(default=None, kw_only=True)
    attributes: Optional[dict] = field(default=None, kw_only=True)


@define
class ExpectedSpans:
    spans: list[ExpectedSpan] = field(kw_only=True)

    def __eq__(self, other_spans: Sequence[ReadableSpan]) -> bool:  # noqa: C901
        # Has expected spans
        span_names = [span.name for span in self.spans]
        other_span_names = [span.name for span in other_spans]
        if sorted(other_span_names) != sorted(span_names):
            raise Exception(f"Expected spans {other_span_names} not found. Found: {span_names}")

        # Has valid trace id
        trace_id = other_spans[0].context.trace_id
        if not trace_id:
            raise Exception(f"Trace id is not set on span {other_spans[0].name}")

        for span in other_spans:
            # All have same trace id
            if span.context.trace_id != trace_id:
                raise Exception(f"Span {span.name} has different trace id than the rest")

            # All have kind set to internal
            if span.kind != SpanKind.INTERNAL:
                raise Exception(f"Span {span.name} is not of kind INTERNAL")

        other_span_by_name = {span.name: span for span in other_spans}
        span_by_name = {span.name: span for span in self.spans}
        expected_status_codes = {span.name: span.status_code for span in self.spans}
        for span_name, status_code in expected_status_codes.items():
            span = other_span_by_name[span_name]
            actual_status_code = span.status.status_code
            if actual_status_code != status_code:
                raise Exception(f"Span {span_name} has code {actual_status_code} instead of {status_code}")

            exception = span_by_name[span_name].exception
            if exception:
                event = span.events[0]
                exc_type = event.attributes.get("exception.type")
                exc_message = event.attributes.get("exception.message")
                exc_stacktrace = event.attributes.get("exception.stacktrace")

                if exc_type != "Exception":
                    raise Exception(f"Span {span_name} does not have exception type Exception")
                if exc_message != str(exception):
                    raise Exception(f"Span {span_name} does not have exception message {exception}")
                if not exc_stacktrace:
                    raise Exception(f"Span {span_name} has no stacktrace")

        expected_parents = {span.name: span.parent for span in self.spans}
        for child, parent in expected_parents.items():
            actual_parent = other_span_by_name[child].parent.span_id if other_span_by_name[child].parent else None
            expected_parent = parent and other_span_by_name[parent].context.span_id
            if actual_parent != expected_parent:
                raise Exception(f"Span {child} has wrong parent")

        expected_attributes_by_span_name = {span.name: span.attributes for span in self.spans}
        for span_name, expected_attributes in expected_attributes_by_span_name.items():
            other_span = other_span_by_name[span_name]
            if expected_attributes is not None and other_span.attributes != expected_attributes:
                raise Exception(
                    f"Span {span_name} has attributes {other_span.attributes} instead of {expected_attributes}"
                )

        return True
