import logging

from griptape.configs import Defaults


class TestLoggingConfig:
    def test_init(self):
        logger = logging.getLogger(Defaults.logging_config.logger_name)
        assert logger.level == logging.INFO
        assert logger.propagate is False
        assert len(logger.handlers) == 1
