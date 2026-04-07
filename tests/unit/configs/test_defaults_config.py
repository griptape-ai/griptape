import pytest


class TestDefaultsConfig:
    def test_init(self):
        from griptape.configs.defaults_config import _DefaultsConfig

        assert _DefaultsConfig() is _DefaultsConfig()

    def test_error_init(self):
        from griptape.configs import Defaults

        with pytest.raises(TypeError):
            Defaults()  # pyright: ignore[reportCallIssue]
