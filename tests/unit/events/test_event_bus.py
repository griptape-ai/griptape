from unittest.mock import Mock

from griptape.events import EventBus, EventListener
from tests.mocks.mock_event import MockEvent


class TestEventBus:
    def test_add_event_listeners(self):
        EventBus.add_event_listeners([EventListener(), EventListener()])
        assert len(EventBus.event_listeners) == 2

    def test_remove_event_listeners(self):
        listeners = [EventListener(), EventListener()]
        EventBus.add_event_listeners(listeners)
        EventBus.remove_event_listeners(listeners)
        assert len(EventBus.event_listeners) == 0

    def test_add_event_listener(self):
        EventBus.add_event_listener(EventListener())
        EventBus.add_event_listener(EventListener())

        assert len(EventBus.event_listeners) == 2

    def test_remove_event_listener(self):
        listener = EventListener()
        EventBus.add_event_listener(listener)
        EventBus.remove_event_listener(listener)

        assert len(EventBus.event_listeners) == 0

    def test_remove_unknown_event_listener(self):
        EventBus.remove_event_listener(EventListener())

    def test_publish_event(self):
        # Given
        mock_handler = Mock()
        mock_handler.return_value = None
        EventBus.add_event_listeners([EventListener(handler=mock_handler)])
        mock_event = MockEvent()

        # When
        EventBus.publish_event(mock_event)

        # Then
        mock_handler.assert_called_once_with(mock_event)
