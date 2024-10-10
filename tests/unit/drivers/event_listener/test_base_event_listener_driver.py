from unittest.mock import MagicMock

from tests.mocks.mock_event import MockEvent
from tests.mocks.mock_event_listener_driver import MockEventListenerDriver


class TestBaseEventListenerDriver:
    def test_publish_event_no_batched(self):
        driver = MockEventListenerDriver(batched=False)
        driver.try_publish_event_payload = MagicMock(side_effect=driver.try_publish_event_payload)

        driver.publish_event(MockEvent().to_dict())

        driver.try_publish_event_payload.assert_called_once()

    def test_publish_event_yes_batched(self):
        driver = MockEventListenerDriver(batched=True)
        driver.try_publish_event_payload_batch = MagicMock(side_effect=driver.try_publish_event_payload)

        for _ in range(0, 9):
            driver.publish_event(MockEvent().to_dict())

        assert len(driver._batch) == 9
        driver.try_publish_event_payload_batch.assert_not_called()

        # Publish the 10th event to trigger the batch publish
        driver.publish_event(MockEvent().to_dict())

        assert len(driver._batch) == 0
        driver.try_publish_event_payload_batch.assert_called_once()

    def test_flush_events(self):
        driver = MockEventListenerDriver(batched=True)
        driver.try_publish_event_payload_batch = MagicMock(side_effect=driver.try_publish_event_payload)

        for _ in range(0, 3):
            driver.publish_event(MockEvent().to_dict())
        assert len(driver.batch) == 3

        driver.flush_events()
        driver.try_publish_event_payload_batch.assert_called_once()
        assert len(driver.batch) == 0
