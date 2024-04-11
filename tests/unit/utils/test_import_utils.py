import pytest
from griptape.utils import import_optional_dependency, is_dependency_installed


class TestImportUtils:
    def test_import_optional_dependency(self):
        assert import_optional_dependency("os")
        assert import_optional_dependency("boto3")

        with pytest.raises(ImportError):
            assert import_optional_dependency("foobar")

    def test_is_dependency_installed(self):
        assert is_dependency_installed("os") is True
        assert is_dependency_installed("boto3") is True

        assert is_dependency_installed("foobar") is False
