import os
import time
from unittest.mock import ANY, MagicMock, Mock

import pytest

from griptape.drivers.event_listener.griptape_cloud_event_listener_driver import GriptapeCloudEventListenerDriver
from griptape.observability.observability import Observability
from tests.mocks.mock_event import MockEvent


class TestGriptapeCloudEventListenerDriver:
    @pytest.fixture(autouse=True)
    def mock_post(self, mocker):
        data = {"data": {"id": "test"}}

        mock_post = mocker.patch("requests.post")
        mock_post.return_value = Mock(status_code=201, json=data)

        return mock_post

    @pytest.fixture()
    def driver(self):
        environ = {
            "GT_CLOUD_BASE_URL": "https://cloud123.griptape.ai",
            "GT_CLOUD_API_KEY": "foo bar",
            "GT_CLOUD_STRUCTURE_RUN_ID": "bar baz",
        }
        original_environ = {}
        for key, value in environ.items():
            original_environ[key] = os.environ.get(key)
            os.environ[key] = value

        yield GriptapeCloudEventListenerDriver()

        for key, value in original_environ.items():
            if value is None:
                del os.environ[key]
            else:
                os.environ[key] = value

    def test_init(self, driver):
        assert driver
        assert driver.api_key == "foo bar"
        assert driver.structure_run_id == "bar baz"

    def test_publish_event_without_span_id(self, mock_post, driver):
        event = MockEvent()
        driver.publish_event(event)
        driver.flush_events()

        time.sleep(1)  # Happens asynchronously, so need to wait for it to finish
        mock_post.assert_called_with(
            url="https://cloud123.griptape.ai/api/structure-runs/bar baz/events",
            json=[driver._get_event_request(event.to_dict())],
            headers={"Authorization": "Bearer foo bar"},
        )

    def test_publish_event_with_span_id(self, mock_post, driver):
        event = MockEvent()
        observability_driver = MagicMock()
        observability_driver.get_span_id.return_value = "test"

        with Observability(observability_driver=observability_driver):
            driver.publish_event(event)
        driver.flush_events()

        time.sleep(1)  # Happens asynchronously, so need to wait for it to finish
        mock_post.assert_called_with(
            url="https://cloud123.griptape.ai/api/structure-runs/bar baz/events",
            json=[driver._get_event_request({**event.to_dict(), "span_id": "test"})],
            headers={"Authorization": "Bearer foo bar"},
        )

    def test_try_publish_event_payload(self, mock_post, driver):
        event = MockEvent()
        driver.try_publish_event_payload(event.to_dict())

        time.sleep(1)  # Happens asynchronously, so need to wait for it to finish
        mock_post.assert_called_once_with(
            url="https://cloud123.griptape.ai/api/structure-runs/bar baz/events",
            json=driver._get_event_request(event.to_dict()),
            headers={"Authorization": "Bearer foo bar"},
        )

    def test_validate_api_key(self):
        with pytest.raises(ValueError, match="No value was found"):
            GriptapeCloudEventListenerDriver()

    def test_validate_run_id(self):
        os.environ["GT_CLOUD_API_KEY"] = "foo bar"

        with pytest.raises(ValueError, match="structure_run_id must be set"):
            GriptapeCloudEventListenerDriver()

    def test_try_publish_event_payload_batch(self, mock_post, driver):
        for _ in range(3):
            event = MockEvent()
            driver.try_publish_event_payload(event.to_dict())

            time.sleep(1)  # Happens asynchronously, so need to wait for it to finish
            mock_post.assert_called_with(
                url="https://cloud123.griptape.ai/api/structure-runs/bar baz/events",
                json=driver._get_event_request(event.to_dict()),
                headers={"Authorization": "Bearer foo bar"},
            )

    @pytest.mark.parametrize(
        ("event", "expected"),
        [
            (
                MockEvent().to_dict(),
                {
                    "payload": {
                        "id": ANY,
                        "meta": {},
                        "timestamp": ANY,
                        "type": "MockEvent",
                    },
                    "timestamp": ANY,
                    "type": "MockEvent",
                },
            ),
            ({}, {"payload": {}, "timestamp": ANY, "type": "UserEvent"}),
        ],
    )
    def test__get_event_request(self, driver, event, expected):
        result = driver._get_event_request(event)

        assert result == expected
