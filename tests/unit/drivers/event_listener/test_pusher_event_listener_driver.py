from pytest import fixture
from tests.mocks.mock_event import MockEvent
from griptape.drivers.event_listener.pusher_event_listener_driver import PusherEventListenerDriver


class TestPusherEventListenerDriver:
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

    def test_try_publish_event_payload_batch(self, driver):
        driver.try_publish_event_payload_batch([MockEvent().to_dict() for _ in range(3)])
