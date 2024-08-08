from unittest.mock import Mock

import pytest

from griptape.events import EventListener, event_bus
from tests.mocks.mock_image_query_driver import MockImageQueryDriver


class TestBaseImageQueryDriver:
    @pytest.fixture()
    def driver(self):
        return MockImageQueryDriver(model="foo")

    def test_query_publishes_events(self, driver):
        mock_handler = Mock()
        event_bus.add_event_listener(EventListener(handler=mock_handler))

        driver.query("foo", [])

        call_args = mock_handler.call_args_list

        args, _kwargs = call_args[0]
        assert args[0].type == "StartImageQueryEvent"

        args, _kwargs = call_args[1]
        assert args[0].type == "FinishImageQueryEvent"
