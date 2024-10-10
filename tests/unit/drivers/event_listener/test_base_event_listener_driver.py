from unittest.mock import MagicMock

from tests.mocks.mock_event import MockEvent
from tests.mocks.mock_event_listener_driver import MockEventListenerDriver


class TestBaseEventListenerDriver:
    def test_publish_event_no_batched(self):
        executor = MagicMock()
        executor.__enter__.return_value = executor
        driver = MockEventListenerDriver(batched=False, futures_executor=executor)
        driver.try_publish_event_payload = MagicMock(side_effect=driver.try_publish_event_payload)
        mock_event_payload = MockEvent().to_dict()

        driver.publish_event(mock_event_payload)

        executor.submit.assert_called_once_with(driver._safe_publish_event_payload, mock_event_payload)

    def test_publish_event_yes_batched(self):
        executor = MagicMock()
        executor.__enter__.return_value = executor
        driver = MockEventListenerDriver(batched=True, futures_executor=executor)
        driver.try_publish_event_payload_batch = MagicMock(side_effect=driver.try_publish_event_payload)
        mock_event_payload = MockEvent().to_dict()

        mock_event_payloads = [mock_event_payload for _ in range(0, 9)]
        for mock_event_payload in mock_event_payloads:
            driver.publish_event(mock_event_payload)

        assert len(driver._batch) == 9
        executor.submit.assert_not_called()
        driver.try_publish_event_payload_batch.assert_not_called()

        # Publish the 10th event to trigger the batch publish
        driver.publish_event(mock_event_payload)

        assert len(driver._batch) == 0
        executor.submit.assert_called_once_with(
            driver._safe_publish_event_payload_batch, [*mock_event_payloads, mock_event_payload]
        )

    def test_flush_events(self):
        executor = MagicMock()
        executor.__enter__.return_value = executor
        driver = MockEventListenerDriver(batched=True, futures_executor=executor)
        driver.try_publish_event_payload_batch = MagicMock(side_effect=driver.try_publish_event_payload)

        mock_event_payloads = [MockEvent().to_dict() for _ in range(0, 3)]
        for mock_event_payload in mock_event_payloads:
            driver.publish_event(mock_event_payload)
        assert len(driver.batch) == 3

        driver.flush_events()
        executor.submit.assert_called_once_with(driver._safe_publish_event_payload_batch, mock_event_payloads)
        assert len(driver.batch) == 0
