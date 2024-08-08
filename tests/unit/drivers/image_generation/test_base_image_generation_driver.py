from unittest.mock import Mock

import pytest

from griptape.artifacts.image_artifact import ImageArtifact
from griptape.events import event_bus
from griptape.events.event_listener import EventListener
from tests.mocks.mock_image_generation_driver import MockImageGenerationDriver


class TestBaseImageGenerationDriver:
    @pytest.fixture()
    def driver(self):
        return MockImageGenerationDriver(model="foo")

    def test_run_text_to_image_publish_events(self, driver):
        mock_handler = Mock()
        event_bus.add_event_listener(EventListener(handler=mock_handler))

        driver.run_text_to_image(
            ["foo", "bar"],
        )

        call_args = mock_handler.call_args_list

        args, _kwargs = call_args[0]
        assert args[0].type == "StartImageGenerationEvent"

        args, _kwargs = call_args[1]
        assert args[0].type == "FinishImageGenerationEvent"

    def test_run_image_variation_publish_events(self, driver):
        mock_handler = Mock()
        event_bus.add_event_listener(EventListener(handler=mock_handler))

        driver.run_image_variation(
            ["foo", "bar"],
            ImageArtifact(
                value="mock image",
                width=512,
                height=512,
                format="png",
            ),
        )

        call_args = mock_handler.call_args_list

        args, _kwargs = call_args[0]
        assert args[0].type == "StartImageGenerationEvent"

        args, _kwargs = call_args[1]
        assert args[0].type == "FinishImageGenerationEvent"

    def test_run_image_image_inpainting_publish_events(self, driver):
        mock_handler = Mock()
        event_bus.add_event_listener(EventListener(handler=mock_handler))

        driver.run_image_inpainting(
            ["foo", "bar"],
            ImageArtifact(
                value="mock image",
                width=512,
                height=512,
                format="png",
            ),
            ImageArtifact(
                value="mock image",
                width=512,
                height=512,
                format="png",
            ),
        )

        call_args = mock_handler.call_args_list

        args, _kwargs = call_args[0]
        assert args[0].type == "StartImageGenerationEvent"

        args, _kwargs = call_args[1]
        assert args[0].type == "FinishImageGenerationEvent"

    def test_run_image_image_outpainting_publish_events(self, driver):
        mock_handler = Mock()
        event_bus.add_event_listener(EventListener(handler=mock_handler))

        driver.run_image_outpainting(
            ["foo", "bar"],
            ImageArtifact(
                value="mock image",
                width=512,
                height=512,
                format="png",
            ),
            ImageArtifact(
                value="mock image",
                width=512,
                height=512,
                format="png",
            ),
        )

        call_args = mock_handler.call_args_list

        args, _kwargs = call_args[0]
        assert args[0].type == "StartImageGenerationEvent"

        args, _kwargs = call_args[1]
        assert args[0].type == "FinishImageGenerationEvent"
