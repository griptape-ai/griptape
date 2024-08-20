import logging

from griptape.config import config
from griptape.config.drivers import OpenAiDriversConfig
from griptape.config.logging import TruncateLoggingFilter
from griptape.structures import Agent

config.drivers_config = OpenAiDriversConfig()

logger = logging.getLogger(config.logging_config.logger_name)
logger.setLevel(logging.ERROR)
logger.addFilter(TruncateLoggingFilter(max_log_length=100))

agent = Agent()
