from unittest.mock import Mock

from griptape.events import EventBus, EventListener
from griptape.events.finish_prompt_event import FinishPromptEvent
from griptape.events.start_prompt_event import StartPromptEvent
from griptape.utils import with_contextvars
from tests.mocks.mock_event import MockEvent


class TestEventBus:
    def test_init(self):
        from griptape.events.event_bus import _EventBus

        assert _EventBus() is _EventBus()

    def test_add_event_listeners_same(self):
        EventBus.add_event_listeners([EventListener(), EventListener()])
        assert len(EventBus.event_listeners) == 1

    def test_add_event_listeners(self):
        EventBus.add_event_listeners([EventListener(on_event=lambda e: e), EventListener()])
        assert len(EventBus.event_listeners) == 2

    def test_remove_event_listeners(self):
        listeners = [EventListener(on_event=lambda e: e), EventListener()]
        EventBus.add_event_listeners(listeners)
        EventBus.remove_event_listeners(listeners)
        assert len(EventBus.event_listeners) == 0

    def test_add_event_listener_same(self):
        EventBus.add_event_listener(EventListener())
        EventBus.add_event_listener(EventListener())
        assert len(EventBus.event_listeners) == 1

    def test_add_event_listener(self):
        EventBus.add_event_listener(EventListener(on_event=lambda e: e))
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
        EventBus.add_event_listeners([EventListener(on_event=mock_handler)])
        mock_event = MockEvent()

        # When
        EventBus.publish_event(mock_event)

        # Then
        mock_handler.assert_called_once_with(mock_event)

    def test_context_manager(self):
        e1 = EventListener()
        EventBus.add_event_listeners([e1])

        with EventListener(lambda e: e) as e2:
            assert EventBus.event_listeners == [e1, e2]

        assert EventBus.event_listeners == [e1]

    def test_context_manager_multiple(self):
        e1 = EventListener()
        EventBus.add_event_listener(e1)

        with EventListener(lambda e: e) as e2, EventListener(lambda e: e) as e3:
            assert EventBus.event_listeners == [e1, e2, e3]

        assert EventBus.event_listeners == [e1]

    def test_nested_context_manager(self):
        e1 = EventListener()
        EventBus.add_event_listener(e1)

        with EventListener(lambda e: e) as e2:
            assert EventBus.event_listeners == [e1, e2]
            with EventListener(lambda e: e) as e3:
                assert EventBus.event_listeners == [e1, e2, e3]
            assert EventBus.event_listeners == [e1, e2]

        assert EventBus.event_listeners == [e1]

    def test_thread_pool_with_context_vars(self):
        from concurrent import futures

        e1 = EventListener(event_types=[StartPromptEvent])
        EventBus.add_event_listener(e1)

        def handler(_) -> None:
            with EventListener(event_types=[FinishPromptEvent]) as e2:
                assert EventBus.event_listeners == [e1, e2]

        with futures.ThreadPoolExecutor() as executor:
            list(executor.map(with_contextvars(handler), range(10)))

        assert EventBus.event_listeners == [e1]

    def test_thread_pool_without_context_vars(self):
        from concurrent import futures

        e1 = EventListener(event_types=[StartPromptEvent])
        EventBus.add_event_listener(e1)

        def handler(_) -> None:
            with EventListener(event_types=[FinishPromptEvent]) as e2:
                assert EventBus.event_listeners == [e2]

        with futures.ThreadPoolExecutor() as executor:
            list(executor.map(handler, range(10)))

        assert EventBus.event_listeners == [e1]

    def test_thread_with_contextvars(self):
        import threading

        e1 = EventListener(lambda e: e)
        EventBus.add_event_listener(e1)

        def handler() -> None:
            assert EventBus.event_listeners == [e1]
            e2 = EventListener(lambda e: e)
            EventBus.add_event_listener(e2)
            assert EventBus.event_listeners == [e1, e2]
            EventBus.remove_event_listener(e2)
            assert EventBus.event_listeners == [e1]
            EventBus.clear_event_listeners()
            assert EventBus.event_listeners == []
            EventBus.add_event_listener(e2)
            assert EventBus.event_listeners == [e2]

        for _ in range(10):
            thread = threading.Thread(target=with_contextvars(handler))
            thread.start()
            thread.join()

        assert EventBus.event_listeners == [e1]

    def test_thread_without_contextvars(self):
        import threading

        e1 = EventListener(lambda e: e)
        EventBus.add_event_listener(e1)

        def handler() -> None:
            assert EventBus.event_listeners == []
            e2 = EventListener(lambda e: e)
            EventBus.add_event_listener(e2)
            assert EventBus.event_listeners == [e2]
            EventBus.remove_event_listener(e2)
            assert EventBus.event_listeners == []
            EventBus.clear_event_listeners()
            assert EventBus.event_listeners == []
            EventBus.add_event_listener(e2)

        for _ in range(10):
            thread = threading.Thread(target=handler)
            thread.start()
            thread.join()

        assert EventBus.event_listeners == [e1]

    def test_coroutine(self):
        import asyncio

        e1 = EventListener(lambda e: e)
        EventBus.add_event_listener(e1)

        async def handler() -> None:
            e2 = EventListener(lambda e: e)
            EventBus.add_event_listener(e2)
            assert EventBus.event_listeners == [e1, e2]
            EventBus.remove_event_listener(e2)
            assert EventBus.event_listeners == [e1]
            EventBus.clear_event_listeners()
            assert EventBus.event_listeners == []
            EventBus.add_event_listener(e2)

        asyncio.run(handler())

        assert EventBus.event_listeners == [e1]
