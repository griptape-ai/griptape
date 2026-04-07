from datetime import datetime, timedelta

import pytest

from griptape.tools import DateTimeTool


class TestDateTimeTool:
    def test_get_current_datetime(self):
        result = DateTimeTool().get_current_datetime({})
        time_delta = datetime.strptime(result.value, "%Y-%m-%d %H:%M:%S.%f") - datetime.now()
        assert abs(time_delta.total_seconds()) <= 1000

    def test_get_past_relative_datetime(self):
        result = DateTimeTool().get_relative_datetime({"values": {"relative_date_string": "5 min ago"}})
        time_delta = datetime.strptime(result.value, "%Y-%m-%d %H:%M:%S.%f") - datetime.now()
        assert abs(time_delta.total_seconds()) <= 1000

        result = DateTimeTool().get_relative_datetime({"values": {"relative_date_string": "2 min ago, 12 seconds"}})
        time_delta = datetime.strptime(result.value, "%Y-%m-%d %H:%M:%S.%f") - datetime.now()
        assert abs(time_delta.total_seconds()) <= 1000

    def test_get_future_relative_datetime(self):
        result = DateTimeTool().get_relative_datetime({"values": {"relative_date_string": "in 1 min, 36 seconds"}})
        time_delta = datetime.strptime(result.value, "%Y-%m-%d %H:%M:%S.%f") - datetime.now()
        assert abs(time_delta.total_seconds()) <= 1000

    def test_get_invalid_relative_datetime(self):
        result = DateTimeTool().get_relative_datetime({"values": {"relative_date_string": "3 days from now"}})
        assert result.type == "ErrorArtifact"

    @pytest.mark.parametrize(
        ("iso_datetime", "timedelta_kwargs", "expected"),
        [
            (
                "2025-01-23T15:09:11.111421",
                {"days": 1, "hours": 2},
                datetime.fromisoformat("2025-01-23T15:09:11.111421") + timedelta(days=1, hours=2),
            ),
            (
                "2025-01-23T15:09:11.111421",
                {"days": -1, "hours": 2},
                datetime.fromisoformat("2025-01-23T15:09:11.111421") + timedelta(days=-1, hours=2),
            ),
        ],
    )
    def test_add_timedelta(self, iso_datetime, timedelta_kwargs, expected):
        result = DateTimeTool().add_timedelta(
            {
                "values": {
                    **({"iso_datetime": iso_datetime} if iso_datetime else {}),
                    **({"timedelta_kwargs": timedelta_kwargs} if timedelta_kwargs else {}),
                }
            }
        )

        assert datetime.fromisoformat(result.value) == expected

    def test_add_timedelta_no_iso_datetime(self):
        result = DateTimeTool().add_timedelta({"values": {"timedelta_kwargs": {"days": 1, "hours": 2}}})

        assert (
            datetime.fromisoformat(result.value) - (datetime.now() + timedelta(days=1, hours=2))
        ).total_seconds() <= 100

    @pytest.mark.parametrize(
        ("start_datetime", "end_datetime", "expected"),
        [
            (
                "2025-01-23T15:09:11.111421",
                "2025-01-24T17:09:11.111421",
                "1 day, 2:00:00",
            ),
            (
                "2025-01-23T15:09:11.111421",
                "2025-01-23T15:09:11.111421",
                "0:00:00",
            ),
            (
                "2025-01-23T15:09:11.111421",
                "2025-01-22T17:09:11.111421",
                "-1 day, 2:00:00",
            ),
        ],
    )
    def test_get_datetime_diff(self, start_datetime, end_datetime, expected):
        result = DateTimeTool().get_datetime_diff(
            {"values": {"start_datetime": start_datetime, "end_datetime": end_datetime}}
        )

        assert result.value == expected
