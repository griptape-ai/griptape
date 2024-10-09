import logging

from griptape.configs.logging import LoggingConfig


class TestLoggingConfig:
    def test_init(self):
        config = LoggingConfig(handlers_formatter=logging.Formatter())

        logger = logging.getLogger(config.logger_name)
        assert logger.level == config.level
        assert logger.propagate == config.propagate
        assert logger.handlers == config.handlers
        assert logger.handlers[0].formatter == config.handlers_formatter
