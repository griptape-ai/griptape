from unittest.mock import MagicMock
import pytest
from collections.abc import Sequence
from griptape.structures import Agent, Pipeline, Workflow
from griptape.tasks import PromptTask
from griptape.utils.observability.griptape_cloud_observability import GriptapeCloudObservability
from opentelemetry.sdk.trace import ReadableSpan
from opentelemetry.trace import SpanKind, StatusCode
from tests.mocks.mock_prompt_driver import MockPromptDriver


class TestGriptapeCloudObservability:
    @pytest.fixture
    def mock_griptape_span_exporter(self, mocker):
        return mocker.patch(
            "griptape.utils.observability.griptape_cloud_observability.GriptapeCloudSpanExporter"
        ).return_value

    def test_agent_never_instrumented(self, mock_griptape_span_exporter):
        agent = Agent(prompt_driver=MockPromptDriver())
        agent.run("Hi")
        mock_griptape_span_exporter.export.assert_not_called()

    def test_agent_instrumented(self, mock_griptape_span_exporter):
        griptape_cloud_observability = GriptapeCloudObservability()
        griptape_cloud_observability.start()
        agent = Agent(prompt_driver=MockPromptDriver())
        agent.run("Hi")
        griptape_cloud_observability.finish()

        class ExpectedSpans:
            def __eq__(self, spans: Sequence[ReadableSpan]):
                def print_spans():
                    for span in spans:
                        print(span.to_json())

                # Has expected spans
                span_names = [span.name for span in spans]
                if sorted(span_names) != sorted(
                    ["Agent.after_run()", "Agent.before_run()", "Agent.run()", "Agent.try_run()", "main"]
                ):
                    print_spans()
                    raise Exception(f"Expected spans not found. Found: {span_names}")

                # Has valid trace id
                trace_id = spans[0].context.trace_id
                if not trace_id:
                    print_spans()
                    raise Exception(f"Trace id is not set on span {span[0].name}")

                for span in spans:
                    # All have same trace id
                    if span.context.trace_id != trace_id:
                        print_spans()
                        raise Exception(f"Span {span.name} has different trace id")

                    # All have kind set to internal
                    if span.kind != SpanKind.INTERNAL:
                        print_spans()
                        raise Exception(f"Span {span.name} is not of kind INTERNAL")

                    # All have status set to OK
                    if span.status.status_code != StatusCode.OK:
                        print_spans()
                        raise Exception(f"Span {span.name} is not of status OK")

                span_by_name = {span.name: span for span in spans}
                expected_parents = {
                    "main": None,
                    "Agent.run()": "main",
                    "Agent.before_run()": "Agent.run()",
                    "Agent.try_run()": "Agent.run()",
                    "Agent.after_run()": "Agent.run()",
                }
                for child, parent in expected_parents.items():
                    actual_parent = span_by_name[child].parent.span_id if span_by_name[child].parent else None
                    expected_parent = parent and span_by_name[parent].context.span_id
                    if actual_parent != expected_parent:
                        raise Exception(f"Span {child} has wrong parent")

                return True

        assert mock_griptape_span_exporter.export.call_count == 1
        mock_griptape_span_exporter.export.assert_called_once_with(ExpectedSpans())

    def test_agent_uninstrumented(self, mock_griptape_span_exporter):
        griptape_cloud_observability = GriptapeCloudObservability()
        griptape_cloud_observability.start()
        griptape_cloud_observability.finish()
        assert mock_griptape_span_exporter.export.call_count == 1
        mock_griptape_span_exporter.export.reset_mock()

        agent = Agent(prompt_driver=MockPromptDriver())
        agent.run("Hi")

        mock_griptape_span_exporter.export.assert_not_called()

    def test_pipeline_instrumented(self, mock_griptape_span_exporter):
        griptape_cloud_observability = GriptapeCloudObservability()
        griptape_cloud_observability.start()
        pipeline = Pipeline(tasks=[PromptTask()], prompt_driver=MockPromptDriver())
        pipeline.run("Hi")
        griptape_cloud_observability.finish()

        class ExpectedSpans:
            def __eq__(self, spans: Sequence[ReadableSpan]):
                def print_spans():
                    for span in spans:
                        print(span.to_json())

                # Has expected spans
                span_names = [span.name for span in spans]
                if sorted(span_names) != sorted(
                    ["Pipeline.after_run()", "Pipeline.before_run()", "Pipeline.run()", "Pipeline.try_run()", "main"]
                ):
                    print_spans()
                    raise Exception(f"Expected spans not found. Found: {span_names}")

                # Has valid trace id
                trace_id = spans[0].context.trace_id
                if not trace_id:
                    print_spans()
                    raise Exception(f"Trace id is not set on span {span[0].name}")

                for span in spans:
                    # All have same trace id
                    if span.context.trace_id != trace_id:
                        print_spans()
                        raise Exception(f"Span {span.name} has different trace id")

                    # All have kind set to internal
                    if span.kind != SpanKind.INTERNAL:
                        print_spans()
                        raise Exception(f"Span {span.name} is not of kind INTERNAL")

                    # All have status set to OK
                    if span.status.status_code != StatusCode.OK:
                        print_spans()
                        raise Exception(f"Span {span.name} is not of status OK")

                span_by_name = {span.name: span for span in spans}
                expected_parents = {
                    "main": None,
                    "Pipeline.run()": "main",
                    "Pipeline.before_run()": "Pipeline.run()",
                    "Pipeline.try_run()": "Pipeline.run()",
                    "Pipeline.after_run()": "Pipeline.run()",
                }
                for child, parent in expected_parents.items():
                    actual_parent = span_by_name[child].parent.span_id if span_by_name[child].parent else None
                    expected_parent = parent and span_by_name[parent].context.span_id
                    if actual_parent != expected_parent:
                        raise Exception(f"Span {child} has wrong parent")

                return True

        assert mock_griptape_span_exporter.export.call_count == 1
        mock_griptape_span_exporter.export.assert_called_once_with(ExpectedSpans())

    def test_workflow_instrumented(self, mock_griptape_span_exporter):
        griptape_cloud_observability = GriptapeCloudObservability()
        griptape_cloud_observability.start()
        workflow = Workflow(tasks=[PromptTask()], prompt_driver=MockPromptDriver())
        workflow.run("Hi")
        griptape_cloud_observability.finish()

        class ExpectedSpans:
            def __eq__(self, spans: Sequence[ReadableSpan]):
                def print_spans():
                    for span in spans:
                        print(span.to_json())

                # Has expected spans
                span_names = [span.name for span in spans]
                if sorted(span_names) != sorted(
                    ["Workflow.after_run()", "Workflow.before_run()", "Workflow.run()", "Workflow.try_run()", "main"]
                ):
                    print_spans()
                    raise Exception(f"Expected spans not found. Found: {span_names}")

                # Has valid trace id
                trace_id = spans[0].context.trace_id
                if not trace_id:
                    print_spans()
                    raise Exception(f"Trace id is not set on span {span[0].name}")

                for span in spans:
                    # All have same trace id
                    if span.context.trace_id != trace_id:
                        print_spans()
                        raise Exception(f"Span {span.name} has different trace id")

                    # All have kind set to internal
                    if span.kind != SpanKind.INTERNAL:
                        print_spans()
                        raise Exception(f"Span {span.name} is not of kind INTERNAL")

                    # All have status set to OK
                    if span.status.status_code != StatusCode.OK:
                        print_spans()
                        raise Exception(f"Span {span.name} is not of status OK")

                span_by_name = {span.name: span for span in spans}
                expected_parents = {
                    "main": None,
                    "Workflow.run()": "main",
                    "Workflow.before_run()": "Workflow.run()",
                    "Workflow.try_run()": "Workflow.run()",
                    "Workflow.after_run()": "Workflow.run()",
                }
                for child, parent in expected_parents.items():
                    actual_parent = span_by_name[child].parent.span_id if span_by_name[child].parent else None
                    expected_parent = parent and span_by_name[parent].context.span_id
                    if actual_parent != expected_parent:
                        raise Exception(f"Span {child} has wrong parent")

                return True

        assert mock_griptape_span_exporter.export.call_count == 1
        mock_griptape_span_exporter.export.assert_called_once_with(ExpectedSpans())

    def test_exception(self, mock_griptape_span_exporter):
        griptape_cloud_observability = GriptapeCloudObservability()
        griptape_cloud_observability.start()
        mock_task = MagicMock()
        mock_task.execute.side_effect = Exception("Boom")
        agent = Agent(tasks=[mock_task], prompt_driver=MockPromptDriver())
        try:
            agent.run("Hi")
        except Exception:
            pass
        griptape_cloud_observability.finish()

        class ExpectedSpans:
            def __eq__(self, spans: Sequence[ReadableSpan]):
                def print_spans():
                    for span in spans:
                        print(span.to_json())

                # Has expected spans
                span_names = [span.name for span in spans]
                if sorted(span_names) != sorted(["Agent.before_run()", "Agent.run()", "Agent.try_run()", "main"]):
                    print_spans()
                    raise Exception(f"Expected spans not found. Found: {span_names}")

                # Has valid trace id
                trace_id = spans[0].context.trace_id
                if not trace_id:
                    print_spans()
                    raise Exception(f"Trace id is not set on span {span[0].name}")

                for span in spans:
                    # All have same trace id
                    if span.context.trace_id != trace_id:
                        print_spans()
                        raise Exception(f"Span {span.name} has different trace id")

                    # All have kind set to internal
                    if span.kind != SpanKind.INTERNAL:
                        print_spans()
                        raise Exception(f"Span {span.name} is not of kind INTERNAL")

                span_by_name = {span.name: span for span in spans}
                expected_status_codes = {
                    "main": StatusCode.OK,
                    "Agent.run()": StatusCode.ERROR,
                    "Agent.before_run()": StatusCode.OK,
                    "Agent.try_run()": StatusCode.ERROR,
                }
                for span_name, status_code in expected_status_codes.items():
                    span = span_by_name[span_name]
                    actual_status_code = span.status.status_code
                    if actual_status_code != status_code:
                        raise Exception(f"Span {span_name} has code {actual_status_code} instead of {status_code}")

                    if status_code == StatusCode.ERROR:
                        event = span.events[0]
                        exc_type = event.attributes.get("exception.type")
                        exc_message = event.attributes.get("exception.message")
                        exc_stacktrace = event.attributes.get("exception.stacktrace")

                        if exc_type != "Exception":
                            raise Exception(f"Span {span_name} has wrong exception type")
                        if exc_message != "Boom":
                            raise Exception(f"Span {span_name} has wrong exception message")
                        if not exc_stacktrace:
                            raise Exception(f"Span {span_name} has no stacktrace")

                expected_parents = {
                    "main": None,
                    "Agent.run()": "main",
                    "Agent.before_run()": "Agent.run()",
                    "Agent.try_run()": "Agent.run()",
                }
                for child, parent in expected_parents.items():
                    actual_parent = span_by_name[child].parent.span_id if span_by_name[child].parent else None
                    expected_parent = parent and span_by_name[parent].context.span_id
                    if actual_parent != expected_parent:
                        raise Exception(f"Span {child} has wrong parent")

                return True

        assert mock_griptape_span_exporter.export.call_count == 1
        mock_griptape_span_exporter.export.assert_called_once_with(ExpectedSpans())
