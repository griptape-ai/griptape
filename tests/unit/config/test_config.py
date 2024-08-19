import pytest

from griptape.config.drivers import OpenAiDriverConfig


class TestConfig:
    @pytest.mark.skip_mock_config()
    def test_init(self):
        from griptape.config import config
        from griptape.config.logging import LoggingConfig

        assert isinstance(config.driver_config, OpenAiDriverConfig)
        assert isinstance(config.logging_config, LoggingConfig)

    @pytest.mark.skip_mock_config()
    def test_lazy_init(self):
        from griptape.config import config

        assert config._driver_config is None
        assert config._logging_config is None

        assert config.driver_config is not None
        assert config.logging_config is not None

        assert config._driver_config is not None
        assert config._logging_config is not None
