from griptape.tools import DateTime
from datetime import datetime


class TestDateTime:
    def test_get_current_datetime(self):
        result = DateTime().get_current_datetime({})
        time_delta = datetime.strptime(result.value, "%Y-%m-%d %H:%M:%S.%f") - datetime.now()
        assert abs(time_delta.total_seconds()) <= 1000
