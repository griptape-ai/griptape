from unittest.mock import ANY, MagicMock

from tests.mocks.mock_event import MockEvent
from tests.mocks.mock_event_listener_driver import MockEventListenerDriver


class TestBaseEventListenerDriver:
    def test_publish_event_no_batched(self):
        executor = MagicMock()
        executor.__enter__.return_value = executor
        driver = MockEventListenerDriver(batched=False, create_futures_executor=lambda: executor)
        mock_event_payload = MockEvent().to_dict()

        driver.publish_event(mock_event_payload)

        executor.submit.assert_called_once_with(ANY, mock_event_payload)

    def test_publish_event_yes_batched(self):
        executor = MagicMock()
        executor.__enter__.return_value = executor
        driver = MockEventListenerDriver(batched=True, create_futures_executor=lambda: executor)
        mock_event_payload = MockEvent().to_dict()

        # Publish 9 events to fill the batch
        mock_event_payloads = [mock_event_payload for _ in range(9)]
        for mock_event_payload in mock_event_payloads:
            driver.publish_event(mock_event_payload)

        assert len(driver._batch) == 9
        executor.submit.assert_not_called()

        # Publish the 10th event to trigger the batch publish
        driver.publish_event(mock_event_payload)

        assert len(driver._batch) == 0
        executor.submit.assert_called_once_with(ANY, [*mock_event_payloads, mock_event_payload])

    def test_flush_events(self):
        executor = MagicMock()
        executor.__enter__.return_value = executor
        driver = MockEventListenerDriver(batched=True, create_futures_executor=lambda: executor)
        driver.try_publish_event_payload_batch = MagicMock(side_effect=driver.try_publish_event_payload)

        driver.flush_events()
        driver.try_publish_event_payload_batch.assert_not_called()
        assert driver.batch == []
        mock_event_payloads = [MockEvent().to_dict() for _ in range(3)]
        for mock_event_payload in mock_event_payloads:
            driver.publish_event(mock_event_payload)
        assert len(driver.batch) == 3

        driver.flush_events()
        executor.submit.assert_called_once_with(ANY, mock_event_payloads)
        assert len(driver.batch) == 0

    def test__safe_publish_event_payload(self):
        mock_fn = MagicMock()
        driver = MockEventListenerDriver(
            batched=False,
            on_event_payload_publish=mock_fn,
        )
        mock_event_payload = MockEvent().to_dict()

        driver._safe_publish_event_payload(mock_event_payload)

        mock_fn.assert_called_once_with(mock_event_payload)

    def test__safe_publish_event_payload_batch(self):
        mock_fn = MagicMock()
        driver = MockEventListenerDriver(
            batched=True,
            on_event_payload_batch_publish=mock_fn,
        )
        mock_event_payloads = [MockEvent().to_dict() for _ in range(3)]

        driver._safe_publish_event_payload_batch(mock_event_payloads)

        mock_fn.assert_called_once_with(mock_event_payloads)

    def test__safe_publish_event_payload_error(self):
        mock_fn = MagicMock()
        driver = MockEventListenerDriver(
            batched=False,
            on_event_payload_publish=mock_fn,
            max_attempts=2,
            max_retry_delay=0.1,
            min_retry_delay=0.1,
        )
        mock_fn.side_effect = Exception("Test Exception")
        mock_event_payload = MockEvent().to_dict()

        driver._safe_publish_event_payload(mock_event_payload)

        assert mock_fn.call_count == driver.max_attempts
        mock_fn.assert_called_with(mock_event_payload)

    def test__safe_publish_event_payload_batch_error(self):
        mock_fn = MagicMock()
        driver = MockEventListenerDriver(
            batched=True,
            on_event_payload_batch_publish=mock_fn,
            max_attempts=2,
            max_retry_delay=0.1,
            min_retry_delay=0.1,
        )
        mock_fn.side_effect = Exception("Test Exception")
        mock_event_payloads = [MockEvent().to_dict() for _ in range(3)]

        driver._safe_publish_event_payload_batch(mock_event_payloads)

        assert mock_fn.call_count == driver.max_attempts
        mock_fn.assert_called_with(mock_event_payloads)
