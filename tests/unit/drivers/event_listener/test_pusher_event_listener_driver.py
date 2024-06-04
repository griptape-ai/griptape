from pytest import fixture
from tests.mocks.mock_event import MockEvent
from griptape.drivers import PusherEventListenerDriver
from unittest.mock import Mock


class TestPusherEventListenerDriver:
    @fixture(autouse=True)
    def mock_post(self, mocker):
        mock_pusher_client = mocker.patch("pusher.Pusher")
        mock_pusher_client.return_value.trigger.return_value = Mock()
        mock_pusher_client.return_value.trigger_batch.return_value = Mock()

        return mock_pusher_client

    @fixture()
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
        driver.try_publish_event_payload(MockEvent().to_dict())

        assert driver.pusher_client.trigger.called_with(
            channels="test-channel", event_name="test-event", data=MockEvent().to_dict()
        )

    def test_try_publish_event_payload_batch(self, driver):
        driver.try_publish_event_payload_batch([MockEvent().to_dict() for _ in range(3)])

        assert driver.pusher_client.trigger_batch.called_with(
            [{"channel": "test-channel", "name": "test-event", "data": MockEvent().to_dict()} for _ in range(3)]
        )
