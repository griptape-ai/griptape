# ruff: noqa: FBT003
import pytest

from griptape.artifacts import BooleanArtifact


class TestBooleanArtifact:
    def test_parse_bool(self):
        assert BooleanArtifact.parse_bool("true").value is True
        assert BooleanArtifact.parse_bool("false").value is False
        assert BooleanArtifact.parse_bool("True").value is True
        assert BooleanArtifact.parse_bool("False").value is False
        assert BooleanArtifact.parse_bool(True).value is True

        with pytest.raises(ValueError):
            BooleanArtifact.parse_bool("foo")

        with pytest.raises(ValueError):
            BooleanArtifact.parse_bool(None)  # pyright: ignore[reportArgumentType]

        assert BooleanArtifact.parse_bool(True).value is True
        assert BooleanArtifact.parse_bool(False).value is False

    def test_add(self):
        with pytest.raises(ValueError):
            BooleanArtifact(True) + BooleanArtifact(True)  # pyright: ignore[reportUnusedExpression]

    def test_value_type_conversion(self):
        assert BooleanArtifact(1).value is True
        assert BooleanArtifact(0).value is False
        assert BooleanArtifact(True).value is True
        assert BooleanArtifact(False).value is False
        assert BooleanArtifact("true").value is True
        assert BooleanArtifact("false").value is True
        assert BooleanArtifact([1]).value is True
        assert BooleanArtifact([]).value is False
        assert BooleanArtifact(False).value is False
        assert BooleanArtifact(True).value is True

    def test_to_text(self):
        assert BooleanArtifact(True).to_text() == "true"
        assert BooleanArtifact(False).to_text() == "false"

    def test__eq__(self):
        assert BooleanArtifact(True) == BooleanArtifact(True)
        assert BooleanArtifact(False) == BooleanArtifact(False)
        assert BooleanArtifact(True) != BooleanArtifact(False)
        assert BooleanArtifact(False) != BooleanArtifact(True)
