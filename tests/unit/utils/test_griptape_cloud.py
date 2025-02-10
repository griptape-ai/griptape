import os

import pytest

from griptape.artifacts import BooleanArtifact, JsonArtifact, TextArtifact
from griptape.drivers.event_listener.griptape_cloud import GriptapeCloudEventListenerDriver
from griptape.events import EventListener
from griptape.events.event_bus import EventBus
from griptape.observability.observability import Observability
from griptape.utils import GriptapeCloudStructure
from tests.mocks.mock_event_listener_driver import MockEventListenerDriver


class TestGriptapeCloudUtils:
    @pytest.fixture(autouse=True)
    def set_up_environment(self):
        os.environ["GT_CLOUD_API_KEY"] = "foo"
        os.environ["GT_CLOUD_STRUCTURE_RUN_ID"] = "bar"

        yield

        del os.environ["GT_CLOUD_API_KEY"]
        del os.environ["GT_CLOUD_STRUCTURE_RUN_ID"]

    @pytest.mark.parametrize("observe", [True, False])
    def test_context_manager(self, observe):
        with GriptapeCloudStructure(observe=observe) as context:
            assert context.in_managed_environment

            assert len(EventBus.event_listeners) == 1
            assert isinstance(EventBus.event_listeners[0].event_listener_driver, GriptapeCloudEventListenerDriver)

            if observe:
                assert Observability.get_global_driver() == context.observability.observability_driver
            else:
                assert Observability.get_global_driver() is None

        assert len(EventBus.event_listeners) == 0
        assert Observability.get_global_driver() is None

    def test_in_managed_environment(self):
        context = GriptapeCloudStructure()

        assert context.in_managed_environment

    def test_structure_run_id(self):
        context = GriptapeCloudStructure()

        assert context.structure_run_id == "bar"

    def test_output(self):
        with GriptapeCloudStructure(
            event_listener=EventListener(event_listener_driver=MockEventListenerDriver())
        ) as context:
            context.output = "foo"
            assert isinstance(context.output, TextArtifact)
            assert context.output.value == "foo"

            context.output = True
            assert isinstance(context.output, BooleanArtifact)
            assert context.output.value is True

            context.output = {"foo": "bar"}
            assert isinstance(context.output, JsonArtifact)
            assert context.output.value == {"foo": "bar"}

            output = TextArtifact("bar")
            context.output = output
            assert context.output is output
