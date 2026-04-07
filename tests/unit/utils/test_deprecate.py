import pytest

from griptape.utils.deprecation import deprecation_warn


class TestDeprecation:
    def test_deprecation_warn(self):
        with pytest.deprecated_call():
            deprecation_warn("This function is deprecated.")
