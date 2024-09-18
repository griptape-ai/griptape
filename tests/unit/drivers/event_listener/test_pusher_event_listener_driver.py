from unittest.mock import Mock

import pytest

from griptape.drivers import PusherEventListenerDriver
from tests.mocks.mock_event import MockEvent


class TestPusherEventListenerDriver:
    @pytest.fixture(autouse=True)
    def mock_post(self, mocker):
        mock_client = mocker.patch("pusher.Pusher")
        mock_client.return_value.trigger.return_value = Mock()
        mock_client.return_value.trigger_batch.return_value = Mock()

        return mock_client

    @pytest.fixture()
    def driver(self):
        return PusherEventListenerDriver(
            app_id="test-app-id",
            key="test-key",
            secret="test-secret",
            cluster="test-cluster",
            channel="test-channel",
            event_name="test-event",
        )

    def test_init(self, driver):
        assert driver

    def test_try_publish_event_payload(self, driver):
        data = MockEvent().to_dict()
        driver.try_publish_event_payload(data)

        driver.client.trigger.assert_called_with(channels="test-channel", event_name="test-event", data=data)

    def test_try_publish_event_payload_batch(self, driver):
        data = [MockEvent().to_dict() for _ in range(3)]
        driver.try_publish_event_payload_batch(data)

        driver.client.trigger_batch.assert_called_with(
            [{"channel": "test-channel", "name": "test-event", "data": data[i]} for i in range(3)]
        )
