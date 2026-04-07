from unittest.mock import Mock

import pytest

from griptape.artifacts import ImageArtifact, TextArtifact
from griptape.artifacts.list_artifact import ListArtifact
from griptape.structures import Agent
from griptape.tasks import BaseTask, OutpaintingImageGenerationTask
from tests.mocks.mock_image_generation_driver import MockImageGenerationDriver


class TestOutpaintingImageGenerationTask:
    @pytest.fixture()
    def text_artifact(self):
        return TextArtifact(value="some text")

    @pytest.fixture()
    def image_artifact(self):
        return ImageArtifact(value=b"some image data", format="png", width=512, height=512)

    def test_artifact_inputs(self, text_artifact: TextArtifact, image_artifact: ImageArtifact):
        input_tuple = (text_artifact, image_artifact, image_artifact)
        task = OutpaintingImageGenerationTask(input_tuple, image_generation_driver=Mock())

        assert task.input.value == list(input_tuple)

    def test_callable_input(self, text_artifact: TextArtifact, image_artifact: ImageArtifact):
        artifacts = [text_artifact, image_artifact, image_artifact]

        def callable_input(task: BaseTask) -> ListArtifact:
            return ListArtifact(artifacts)

        task = OutpaintingImageGenerationTask(callable_input, image_generation_driver=Mock())

        assert task.input.value == artifacts

    def test_list_input(self, text_artifact: TextArtifact, image_artifact: ImageArtifact):
        artifacts = [text_artifact, image_artifact]
        task = OutpaintingImageGenerationTask(ListArtifact(artifacts), image_generation_driver=Mock())

        assert task.input.value == artifacts

    def test_bad_input(self, image_artifact):
        with pytest.raises(ValueError):
            OutpaintingImageGenerationTask(("foo", "bar", image_artifact)).try_run()  # pyright: ignore[reportArgumentType]

        with pytest.raises(ValueError):
            OutpaintingImageGenerationTask(("foo", image_artifact, "baz")).try_run()  # pyright: ignore[reportArgumentType]

    def test_run(self, text_artifact, image_artifact):
        mock_driver = MockImageGenerationDriver()
        task = OutpaintingImageGenerationTask(
            (text_artifact, image_artifact, image_artifact), image_generation_driver=mock_driver
        )
        output = task.run()

        assert output.value == b"mock image"

    def test_config_image_generation_driver(self, text_artifact, image_artifact):
        task = OutpaintingImageGenerationTask((text_artifact, image_artifact, image_artifact))
        Agent().add_task(task)

        assert isinstance(task.image_generation_driver, MockImageGenerationDriver)
