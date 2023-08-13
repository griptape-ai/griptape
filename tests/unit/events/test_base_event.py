import datetime
from tests.mocks.mock_event import MockEvent


class TestBaseEvent:
    def test_timestamp(self):
        dt = datetime.datetime.now()

        assert MockEvent().timestamp is not None
        assert MockEvent(timestamp=dt).timestamp == dt
        