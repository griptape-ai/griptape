import pytest

from griptape.artifacts import TextArtifact
from griptape.rules import Rule, Ruleset
from tests.mocks.mock_image_generation_task import MockImageGenerationTask


class TestBaseImageGenerationTask:
    def test_validate_negative_rulesets(self) -> None:
        assert MockImageGenerationTask(
            TextArtifact("some input"),
            negative_rulesets=[Ruleset(name="Negative Ruleset", rules=[Rule(value="Negative Rule")])],
            output_dir="some/dir",
        )

    def test_validate_negative_rules(self) -> None:
        assert MockImageGenerationTask(
            TextArtifact("some input"), negative_rules=[Rule(value="Negative Rule")], output_dir="some/dir"
        )

    def test_negative_rulesets_from_rulesets(self) -> None:
        ruleset = Ruleset(name="Negative Ruleset", rules=[Rule(value="Negative Rule")])

        task = MockImageGenerationTask(TextArtifact("some input"), negative_rulesets=[ruleset], output_dir="some/dir")

        assert task.negative_rulesets[0] == ruleset

    def test_negative_rulesets_from_rules(self) -> None:
        rule = Rule(value="Negative Rule")

        task = MockImageGenerationTask(TextArtifact("some input"), negative_rules=[rule], output_dir="some/dir")

        assert task.negative_rulesets[0].name == task.DEFAULT_NEGATIVE_RULESET_NAME
        assert task.negative_rulesets[0].rules[0] == rule

    def test_validate_output_dir(self) -> None:
        with pytest.raises(ValueError):
            MockImageGenerationTask(TextArtifact("some input"), output_dir="some/dir", output_file="some/file")

    def test__get_prompts(self):
        task = MockImageGenerationTask(
            TextArtifact("some input"), rulesets=[Ruleset(name="Ruleset", rules=[Rule(value="Rule")])]
        )

        assert task._get_prompts(task.input.to_text()) == ["some input", "Rule"]

    def test__get_negative_prompts(self):
        task = MockImageGenerationTask(
            TextArtifact("some input"),
            negative_rulesets=[Ruleset(name="Negative Ruleset", rules=[Rule(value="Negative Rule")])],
        )

        assert task._get_negative_prompts() == ["Negative Rule"]
