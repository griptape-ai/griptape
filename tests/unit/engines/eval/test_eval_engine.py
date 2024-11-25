import json

import pytest
from attrs import validators

from griptape.engines import EvalEngine
from tests.mocks.mock_prompt_driver import MockPromptDriver


class TestEvalEngine:
    @pytest.fixture()
    def engine(self):
        return EvalEngine(
            criteria="foo",
            prompt_driver=MockPromptDriver(
                mock_output=json.dumps(
                    {
                        "steps": ["mock output"],
                        "score": 0.0,
                        "reason": "mock output",
                    }
                ),
            ),
        )

    def test_generate_evaluation_steps(self):
        engine = EvalEngine(
            criteria="foo",
            prompt_driver=MockPromptDriver(
                mock_output=json.dumps(
                    {
                        "steps": ["mock output"],
                    }
                ),
            ),
        )
        assert engine.evaluation_steps == ["mock output"]

    def test_validate_criteria(self):
        with pytest.raises(ValueError, match="either criteria or evaluation_steps must be specified"):
            assert EvalEngine(criteria=None)

        assert EvalEngine(
            criteria="foo",
            prompt_driver=MockPromptDriver(
                mock_output=json.dumps(
                    {
                        "steps": ["mock output"],
                    }
                ),
            ),
        )
        with pytest.raises(ValueError, match="can't have both criteria and evaluation_steps specified"):
            assert EvalEngine(
                criteria="foo",
                evaluation_steps=["foo"],
            )

        with pytest.raises(ValueError, match="criteria must not be empty"):
            assert EvalEngine(criteria="")

    def test_validate_evaluation_steps(self):
        # `criteria` validators run first so to test `evaluation_steps` validators
        # we must disable the `criteria` validators.
        with validators.disabled():
            engine = EvalEngine(evaluation_steps=[])
        with pytest.raises(ValueError, match="either evaluation_steps or criteria must be specified"):
            engine.evaluation_steps = None

        assert EvalEngine(
            evaluation_steps=["foo"],
        )
        with pytest.raises(ValueError, match="can't have both criteria and evaluation_steps specified"):
            assert EvalEngine(
                evaluation_steps=["foo"],
                criteria="foo",
            )

        with pytest.raises(ValueError, match="evaluation_steps must not be empty"):
            assert EvalEngine(evaluation_steps=[])

    def test_validate_evaluation_params(self):
        with pytest.raises(ValueError, match="evaluation_params must not be empty"):
            assert EvalEngine(evaluation_steps=["foo"], evaluation_params=[])

        with pytest.raises(ValueError, match="Input is required in evaluation_params"):
            assert EvalEngine(evaluation_steps=["foo"], evaluation_params=[EvalEngine.Param.EXPECTED_OUTPUT])

        with pytest.raises(ValueError, match="Actual Output is required in evaluation_params"):
            assert EvalEngine(evaluation_steps=["foo"], evaluation_params=[EvalEngine.Param.INPUT])

    def test_evaluate(self):
        engine = EvalEngine(
            evaluation_steps=["foo"],
            prompt_driver=MockPromptDriver(
                mock_output=json.dumps(
                    {
                        "score": 0.0,
                        "reason": "mock output",
                    }
                ),
            ),
        )
        score, reason = engine.evaluate(
            input="foo",
            expected_output="bar",
            actual_output="baz",
        )

        assert score == 0.0
        assert reason == "mock output"

    def test_evaluate_invalid_param(self, engine):
        with pytest.raises(ValueError, match="All keys in kwargs must be a member of EvalEngine.Param"):
            engine.evaluate(foo="bar")

    def test_evaluate_missing_input(self, engine):
        with pytest.raises(ValueError, match="Input is required for evaluation"):
            engine.evaluate()

    def test_evaluate_missing_actual_output(self, engine):
        with pytest.raises(ValueError, match="Actual Output is required for evaluation"):
            engine.evaluate(input="foo")
