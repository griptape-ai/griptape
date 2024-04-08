from moto import mock_iotdata
from unittest.mock import Mock
from tests.mocks.mock_event import MockEvent
from griptape.drivers.event_listener.local_event_listener_driver import LocalEventListenerDriver


@mock_iotdata
class TestLocalEventListenerDriver:
    def test_try_publish_event(self):
        mock = Mock()
        event = MockEvent()
        driver = LocalEventListenerDriver(handler=mock)
        driver.try_publish_event(event=event)
        mock.assert_called_once_with({"event": event.to_dict()})
