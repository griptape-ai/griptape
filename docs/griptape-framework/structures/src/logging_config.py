import logging

from griptape.configs import Defaults
from griptape.configs.drivers import OpenAiDriversConfig
from griptape.configs.logging import TruncateLoggingFilter
from griptape.structures import Agent

Defaults.drivers_config = OpenAiDriversConfig()

logger = logging.getLogger(Defaults.logging_config.logger_name)
logger.setLevel(logging.ERROR)
logger.addFilter(TruncateLoggingFilter(max_log_length=100))

agent = Agent()
