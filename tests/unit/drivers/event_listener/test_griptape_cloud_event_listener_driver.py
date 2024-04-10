from unittest.mock import Mock
from pytest import fixture
import pytest
from tests.mocks.mock_event import MockEvent
from griptape.drivers.event_listener.griptape_cloud_event_listener_driver import GriptapeCloudEventListenerDriver


class TestGriptapeCloudEventListenerDriver:
    @fixture(autouse=True)
    def mock_post(self, mocker):
        data = {"data": {"id": "test"}}

        mock_post = mocker.patch("requests.post")
        mock_post.return_value = Mock(status_code=201, json=data)

        return mock_post

    @fixture()
    def driver(self):
        return GriptapeCloudEventListenerDriver(api_key="foo bar", run_id="baz")

    def test_init(self, driver):
        assert driver

    def test_try_publish_event(self, mock_post, driver):
        event = MockEvent()
        driver.try_publish_event(event=event)

        mock_post.assert_called_once_with(
            url=f"https://cloud.griptape.ai/api/runs/{driver.run_id}/events",
            json=event.to_dict(),
            headers={"Authorization": "Bearer foo bar"},
        )

    def test_no_run_id(self):
        with pytest.raises(ValueError):
            GriptapeCloudEventListenerDriver(api_key="foo bar")
