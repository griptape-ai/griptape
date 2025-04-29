import json

import pytest
import schema
from pydantic import create_model

from griptape.artifacts.json_artifact import JsonArtifact
from griptape.artifacts.model_artifact import ModelArtifact
from griptape.tasks import OutputSchemaValidationSubtask, PromptTask
from tests.mocks.mock_prompt_driver import MockPromptDriver, PromptStack
from tests.mocks.mock_tool.tool import ErrorArtifact, TextArtifact


class TestOutputSchemaValidationSubtask:
    @pytest.fixture(
        params=[
            schema.Schema({"key": str}),
            create_model("OutputSchema", key=(str, ...)),
        ]
    )
    def output_schema(self, request):
        return request.param

    @pytest.mark.parametrize(
        ("input_value", "output_schema", "expected_output_value", "expected_validation_errors"),
        [
            (
                {"key": "value"},
                create_model("OutputSchema", key=(str, ...)),
                {"key": "value"},
                None,
            ),
            (
                {"key": 123},
                create_model("OutputSchema", key=(str, ...)),
                None,
                "[{'type': 'string_type', 'loc': ('key',), 'msg': 'Input should be a valid string', 'input': 123, 'url': 'https://errors.pydantic.dev/2.11/v/string_type'}]",
            ),
            (
                {"key": "value"},
                schema.Schema({"key": str}),
                {"key": "value"},
                None,
            ),
            (
                {"key": 123},
                schema.Schema({"key": str}),
                None,
                "Key 'key' error:\n123 should be instance of 'str'",
            ),
        ],
    )
    @pytest.mark.parametrize(
        ("structured_output_strategy"),
        [
            "native",
            "tool",
            "rule",
        ],
    )
    def test_attach_to(
        self, input_value, structured_output_strategy, expected_output_value, expected_validation_errors, output_schema
    ):
        origin_task = PromptTask(
            prompt_driver=MockPromptDriver(
                structured_output_strategy=structured_output_strategy,
            ),
        )
        subtask = OutputSchemaValidationSubtask(
            input=TextArtifact(json.dumps(input_value)),
            output_schema=output_schema,
            structured_output_strategy=structured_output_strategy,
        )

        subtask.attach_to(origin_task)

        if structured_output_strategy in ("native", "rule"):
            if expected_output_value is None:
                assert subtask.output == expected_output_value
            else:
                assert subtask.output is not None
                if isinstance(output_schema, schema.Schema):
                    assert isinstance(subtask.output, JsonArtifact)
                    assert subtask.output.value == expected_output_value
                else:
                    assert isinstance(subtask.output, ModelArtifact)
                    assert subtask.output.value.model_dump() == expected_output_value
            assert subtask.validation_errors == expected_validation_errors
        else:
            assert subtask.output is not None
            assert subtask.output.value == json.dumps(input_value)

    def test_before_run(self):
        subtask = OutputSchemaValidationSubtask(
            input=TextArtifact("input"),
            output_schema=create_model("OutputSchema", key=(str, ...)),
        )

        assert subtask.before_run() is None

    @pytest.mark.parametrize(
        "validation_errors",
        [
            None,
            "Validation error",
        ],
    )
    def test_try_run(self, validation_errors):
        subtask = OutputSchemaValidationSubtask(
            input=TextArtifact("input"),
            output_schema=create_model("OutputSchema", key=(str, ...)),
        )
        subtask._validation_errors = validation_errors

        result = subtask.try_run()

        if validation_errors is None:
            assert result == subtask.input
        else:
            assert isinstance(result, ErrorArtifact)
            assert result.value == f"Validation error: {validation_errors}"

    def test_after_run(self):
        subtask = OutputSchemaValidationSubtask(
            input=TextArtifact("input"),
            output_schema=create_model("OutputSchema", key=(str, ...)),
        )

        assert subtask.after_run() is None

    @pytest.mark.parametrize(
        "output",
        [
            None,
            TextArtifact("output"),
        ],
    )
    def test_add_to_prompt_stack(self, output):
        subtask = OutputSchemaValidationSubtask(
            input=TextArtifact("input"),
            output_schema=create_model("OutputSchema", key=(str, ...)),
        )
        subtask.output = output
        stack = PromptStack()

        subtask.add_to_prompt_stack(stack)

        if output is None:
            assert len(stack.messages) == 0
        else:
            assert len(stack.messages) == 2
            assert stack.messages[0].role == "assistant"
            assert stack.messages[0].content[0].artifact.value == subtask.generate_assistant_subtask_template(subtask)
            assert stack.messages[1].role == "user"
            assert stack.messages[1].content[0].artifact.value == subtask.generate_user_subtask_template(subtask)
