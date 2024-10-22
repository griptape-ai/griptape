import threading
from unittest.mock import Mock

from griptape.events import EventBus, EventListener
from tests.mocks.mock_event import MockEvent


class TestEventBus:
    def test_init(self):
        from griptape.events.event_bus import _EventBus

        assert _EventBus() is _EventBus()

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

    def test_thread_locality(self):
        from griptape.events.event_bus import _EventBus

        def thread_routine(thread_results, index):
            # Each thread gets its own _EventBus instance
            bus = _EventBus()
            bus.add_event_listener(EventListener())
            thread_results[index] = bus

        thread_results = [None, None]

        thread1 = threading.Thread(target=thread_routine, args=(thread_results, 0))
        thread2 = threading.Thread(target=thread_routine, args=(thread_results, 1))

        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()

        assert thread_results[0] is not None
        assert thread_results[1] is not None
        # Check that each thread has its own instance of _EventBus
        assert thread_results[0] is not thread_results[1]
        # Ensure that changes in one thread don't affect the other
        assert thread_results[0].event_listeners is not thread_results[1].event_listeners
