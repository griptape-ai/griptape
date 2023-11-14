from unittest.mock import Mock

import pytest

from griptape.rules import Ruleset, Rule
from griptape.tasks import ImageGenerationTask


class TestImageGenerationTask:
    @pytest.fixture
    def engine(self):
        return Mock()

    def test_validate_negative_rulesets(self, engine):
        with pytest.raises(ValueError):
            ImageGenerationTask(
                image_generation_engine=engine,
                negative_rulesets=[Ruleset(name="Negative Ruleset", rules=[Rule(value="Negative Rule")])],
                negative_rules=[Rule(value="Negative Rule")],
            )

        assert ImageGenerationTask(
            image_generation_engine=engine,
            negative_rulesets=[Ruleset(name="Negative Ruleset", rules=[Rule(value="Negative Rule")])],
        )

    def test_validate_negative_rules(self, engine):
        with pytest.raises(ValueError):
            ImageGenerationTask(
                image_generation_engine=engine,
                negative_rulesets=[Ruleset(name="Negative Ruleset", rules=[Rule(value="Negative Rule")])],
                negative_rules=[Rule(value="Negative Rule")],
            )

        assert ImageGenerationTask(image_generation_engine=engine, negative_rules=[Rule(value="Negative Rule")])

    def test_all_negative_rulesets_from_rulesets(self, engine):
        ruleset = Ruleset(name="Negative Ruleset", rules=[Rule(value="Negative Rule")])

        task = ImageGenerationTask(image_generation_engine=engine, negative_rulesets=[ruleset])

        assert task.all_negative_rulesets[0] == ruleset

    def test_all_negative_rulesets_from_rules(self, engine):
        rule = Rule(value="Negative Rule")

        task = ImageGenerationTask(image_generation_engine=engine, negative_rules=[rule])

        assert task.all_negative_rulesets[0].name == task.NEGATIVE_RULESET_NAME
        assert task.all_negative_rulesets[0].rules[0] == rule
