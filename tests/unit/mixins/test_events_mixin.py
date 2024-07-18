from unittest.mock import Mock

import pytest

from griptape.events import EventListener
from griptape.mixins import EventPublisherMixin
from tests.mocks.mock_event import MockEvent


class TestEventsMixin:
    def test_init(self):
        assert EventPublisherMixin()

    def test_add_event_listeners(self):
        mixin = EventPublisherMixin()

        mixin.add_event_listeners([EventListener(), EventListener()])
        assert len(mixin.event_listeners) == 2

    def test_remove_event_listeners(self):
        mixin = EventPublisherMixin()

        listeners = [EventListener(), EventListener()]
        mixin.add_event_listeners(listeners)
        mixin.remove_event_listeners(listeners)
        assert len(mixin.event_listeners) == 0

    def test_add_event_listener(self):
        mixin = EventPublisherMixin()

        mixin.add_event_listener(EventListener())
        mixin.add_event_listener(EventListener())

        assert len(mixin.event_listeners) == 2

    def test_remove_event_listener(self):
        mixin = EventPublisherMixin()

        listener = EventListener()
        mixin.add_event_listener(listener)
        mixin.remove_event_listener(listener)

        assert len(mixin.event_listeners) == 0

    def test_remove_unknown_event_listener(self):
        mixin = EventPublisherMixin()

        with pytest.raises(ValueError):
            mixin.remove_event_listener(EventListener())

    def test_publish_event(self):
        # Given
        mock_handler = Mock()
        mock_handler.return_value = None
        mixin = EventPublisherMixin(event_listeners=[EventListener(handler=mock_handler)])
        mock_event = MockEvent()

        # When
        mixin.publish_event(mock_event)

        # Then
        mock_handler.assert_called_once_with(mock_event)
