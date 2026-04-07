from unittest.mock import Mock

import pytest

from griptape.drivers.event_listener.webhook_event_listener_driver import WebhookEventListenerDriver
from tests.mocks.mock_event import MockEvent


class TestWebhookEventListenerDriver:
    @pytest.fixture(autouse=True)
    def mock_post(self, mocker):
        mock_post = mocker.patch("requests.post")
        mock_post.return_value = Mock(status_code=201)

        return mock_post

    def test_init(self):
        assert WebhookEventListenerDriver(webhook_url="")

    def test_try_publish_event_payload(self, mock_post):
        driver = WebhookEventListenerDriver(webhook_url="foo bar", headers={"Authorization": "Bearer foo bar"})
        event = MockEvent()
        driver.try_publish_event_payload(event.to_dict())

        mock_post.assert_called_once_with(
            url="foo bar", json=event.to_dict(), headers={"Authorization": "Bearer foo bar"}
        )

    def test_try_publish_event_payload_batch(self, mock_post):
        driver = WebhookEventListenerDriver(webhook_url="foo bar", headers={"Authorization": "Bearer foo bar"})

        for _ in range(3):
            event = MockEvent()
            driver.try_publish_event_payload(event.to_dict())

            mock_post.assert_called_with(
                url="foo bar", json=event.to_dict(), headers={"Authorization": "Bearer foo bar"}
            )
