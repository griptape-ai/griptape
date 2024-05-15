import os
from unittest.mock import Mock

import pytest
from pytest import fixture

from griptape.drivers.event_listener.griptape_cloud_event_listener_driver import GriptapeCloudEventListenerDriver
from tests.mocks.mock_event import MockEvent


class TestGriptapeCloudEventListenerDriver:
    @fixture(autouse=True)
    def mock_post(self, mocker):
        data = {"data": {"id": "test"}}

        mock_post = mocker.patch("requests.post")
        mock_post.return_value = Mock(status_code=201, json=data)

        return mock_post

    @fixture()
    def driver(self):
        os.environ["GT_CLOUD_BASE_URL"] = "https://cloud123.griptape.ai"

        return GriptapeCloudEventListenerDriver(api_key="foo bar", structure_run_id="bar baz")

    def test_init(self, driver):
        assert driver
        assert driver.api_key == "foo bar"
        assert driver.structure_run_id == "bar baz"

    def test_try_publish_event_payload(self, mock_post, driver):
        event = MockEvent()
        driver.try_publish_event_payload(event.to_dict())

        mock_post.assert_called_once_with(
            url="https://cloud123.griptape.ai/api/structure-runs/bar baz/events",
            json=event.to_dict(),
            headers={"Authorization": "Bearer foo bar"},
        )

    def try_publish_event_payload_batch(self, mock_post, driver):
        for _ in range(3):
            event = MockEvent()
            driver.try_publish_event_payload(event.to_dict())

            mock_post.assert_called_with(
                url="https://cloud123.griptape.ai/api/structure-runs/bar baz/events",
                json=event.to_dict(),
                headers={"Authorization": "Bearer foo bar"},
            )

    def test_no_structure_run_id(self):
        with pytest.raises(ValueError):
            GriptapeCloudEventListenerDriver(api_key="foo bar")
