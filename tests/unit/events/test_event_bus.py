from unittest.mock import Mock

from griptape.events import EventListener, event_bus
from tests.mocks.mock_event import MockEvent


class TestEventBus:
    def test_add_event_listeners(self):
        event_bus.add_event_listeners([EventListener(), EventListener()])
        assert len(event_bus.event_listeners) == 2

    def test_remove_event_listeners(self):
        listeners = [EventListener(), EventListener()]
        event_bus.add_event_listeners(listeners)
        event_bus.remove_event_listeners(listeners)
        assert len(event_bus.event_listeners) == 0

    def test_add_event_listener(self):
        event_bus.add_event_listener(EventListener())
        event_bus.add_event_listener(EventListener())

        assert len(event_bus.event_listeners) == 2

    def test_remove_event_listener(self):
        listener = EventListener()
        event_bus.add_event_listener(listener)
        event_bus.remove_event_listener(listener)

        assert len(event_bus.event_listeners) == 0

    def test_remove_unknown_event_listener(self):
        event_bus.remove_event_listener(EventListener())

    def test_publish_event(self):
        # Given
        mock_handler = Mock()
        mock_handler.return_value = None
        event_bus.add_event_listeners([EventListener(handler=mock_handler)])
        mock_event = MockEvent()

        # When
        event_bus.publish_event(mock_event)

        # Then
        mock_handler.assert_called_once_with(mock_event)
