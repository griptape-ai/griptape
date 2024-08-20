import io
import logging
from contextlib import redirect_stdout

from griptape.configs import Defaults
from griptape.configs.logging import NewlineLoggingFilter
from griptape.structures import Agent


class TestNewlineLoggingFilter:
    def test_filter(self):
        # use the filter in an Agent
        logger = logging.getLogger(Defaults.logging_config.logger_name)
        logger.addFilter(NewlineLoggingFilter(replace_str="$$$"))
        agent = Agent()
        # use a context manager to capture the stdout
        with io.StringIO() as buf, redirect_stdout(buf):
            agent.run()
            output = buf.getvalue()
            assert "$$$" in output
