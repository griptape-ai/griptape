import logging

from griptape.configs.logging import JsonFormatter


class TestJsonFormatter:
    def test_init(self):
        formatter = JsonFormatter()
        assert formatter

    def test_format(self):
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="name",
            level=logging.INFO,
            pathname="pathname",
            lineno=1,
            msg={"key": "value"},
            args=None,
            exc_info=None,
        )
        assert formatter.format(record) == '{\n  "key": "value"\n}'
