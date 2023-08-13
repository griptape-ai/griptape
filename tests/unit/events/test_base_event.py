import time
from tests.mocks.mock_event import MockEvent


class TestBaseEvent:
    def test_timestamp(self):
        dt = time.time()

        assert MockEvent(timestamp=dt).timestamp == dt
        assert MockEvent().timestamp >= dt
