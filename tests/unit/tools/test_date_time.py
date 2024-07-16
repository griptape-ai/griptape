from datetime import datetime

from griptape.tools import DateTime


class TestDateTime:
    def test_get_current_datetime(self):
        result = DateTime().get_current_datetime({})
        time_delta = datetime.strptime(result.value, "%Y-%m-%d %H:%M:%S.%f") - datetime.now()
        assert abs(time_delta.total_seconds()) <= 1000

    def test_get_past_relative_datetime(self):
        result = DateTime().get_relative_datetime({"values": {"relative_date_string": "5 min ago"}})
        time_delta = datetime.strptime(result.value, "%Y-%m-%d %H:%M:%S.%f") - datetime.now()
        assert abs(time_delta.total_seconds()) <= 1000

        result = DateTime().get_relative_datetime({"values": {"relative_date_string": "2 min ago, 12 seconds"}})
        time_delta = datetime.strptime(result.value, "%Y-%m-%d %H:%M:%S.%f") - datetime.now()
        assert abs(time_delta.total_seconds()) <= 1000

    def test_get_future_relative_datetime(self):
        result = DateTime().get_relative_datetime({"values": {"relative_date_string": "in 1 min, 36 seconds"}})
        time_delta = datetime.strptime(result.value, "%Y-%m-%d %H:%M:%S.%f") - datetime.now()
        assert abs(time_delta.total_seconds()) <= 1000

    def test_get_invalid_relative_datetime(self):
        result = DateTime().get_relative_datetime({"values": {"relative_date_string": "3 days from now"}})
        assert result.type == "ErrorArtifact"
