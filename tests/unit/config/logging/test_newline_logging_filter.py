import io
import logging
from contextlib import redirect_stdout

from griptape.config import config
from griptape.config.logging import NewlineLoggingFilter
from griptape.structures import Agent


class TestNewlineLoggingFilter:
    def test_filter(self):
        # use the filter in an Agent
        logger = logging.getLogger(config.logging_config.logger_name)
        logger.addFilter(NewlineLoggingFilter(replace_str="$$$"))
        agent = Agent()
        # use a context manager to capture the stdout
        with io.StringIO() as buf, redirect_stdout(buf):
            agent.run()
            output = buf.getvalue()
            assert "$$$" in output
