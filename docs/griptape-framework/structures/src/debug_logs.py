import logging

from griptape.configs import Defaults
from griptape.configs.logging import JsonFormatter
from griptape.structures import Agent

logger = logging.getLogger(Defaults.logging_config.logger_name)
logger.setLevel(logging.DEBUG)
logger.handlers[0].setFormatter(JsonFormatter())

agent = Agent()

agent.run("Hello world!")
