from unittest.mock import Mock

import pytest
from griptape.tasks import BaseTask, ImageVariationTask
from griptape.artifacts import TextArtifact, ImageArtifact


class TestImageVariationTask:
    @pytest.fixture
    def text_artifact(self):
        return TextArtifact(value="some text")

    @pytest.fixture
    def image_artifact(self):
        return ImageArtifact(value=b"some image data", mime_type="image/png", width=512, height=512)

    def test_artifact_inputs(self, text_artifact, image_artifact):
        input_tuple = (text_artifact, image_artifact)
        task = ImageVariationTask(input=input_tuple, image_generation_engine=Mock())

        assert task.input == input_tuple

    def test_callable_input(self, text_artifact, image_artifact):
        input_tuple = (text_artifact, image_artifact)

        def callable(task: BaseTask) -> (TextArtifact, ImageArtifact):
            return input_tuple

        task = ImageVariationTask(input=callable, image_generation_engine=Mock())

        assert task.input == input_tuple
