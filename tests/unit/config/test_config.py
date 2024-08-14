import pytest

from griptape.config.openai_driver_config import OpenAiDriverConfig


class TestConfig:
    @pytest.mark.skip_autouse_fixture()
    def test_init(self):
        from griptape.config import LoggingConfig, config

        assert isinstance(config.drivers, OpenAiDriverConfig)
        assert isinstance(config.logging, LoggingConfig)

    @pytest.mark.skip_autouse_fixture()
    def test_lazy_init(self):
        from griptape.config import config

        assert config._drivers is None
        assert config._logging is None

        assert config.drivers is not None
        assert config.logging is not None

        assert config._drivers is not None
        assert config._logging is not None
