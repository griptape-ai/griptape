import pytest
from griptape.utils.decorators import deprecated


class TestDecorators:
    def test_deprecated(self):
        @deprecated("This function is deprecated")
        def test_function():
            pass

        with pytest.deprecated_call():
            test_function()
