from griptape.engines import ImageQueryEngine

import pytest
from griptape.tasks import BaseTask, ImageQueryTask
from griptape.artifacts import TextArtifact, ImageArtifact
from griptape.structures import Agent
from tests.mocks.mock_image_query_driver import MockImageQueryDriver
from tests.mocks.mock_structure_config import MockStructureConfig


class TestImageQueryTask:
    @pytest.fixture
    def text_artifact(self):
        return TextArtifact(value="some text")

    @pytest.fixture
    def image_artifact(self):
        return ImageArtifact(value=b"some image data", mime_type="image/png", width=512, height=512)

    def test_text_inputs(self, text_artifact: TextArtifact, image_artifact: ImageArtifact):
        task = ImageQueryTask((text_artifact.value, [image_artifact, image_artifact]))

        assert task.input[0].value == text_artifact.value
        assert task.input[1] == [image_artifact, image_artifact]

    def test_artifact_inputs(self, text_artifact: TextArtifact, image_artifact: ImageArtifact):
        input_tuple = (text_artifact, [image_artifact, image_artifact])
        task = ImageQueryTask(input_tuple)

        assert task.input == input_tuple

    def test_callable_input(self, text_artifact: TextArtifact, image_artifact: ImageArtifact):
        input_tuple = (text_artifact, [image_artifact, image_artifact])

        def callable(task: BaseTask) -> tuple[TextArtifact, list[ImageArtifact]]:
            return input_tuple

        task = ImageQueryTask(callable)

        assert task.input == input_tuple

    def test_config_image_generation_engine(self, text_artifact, image_artifact):
        task = ImageQueryTask((text_artifact, [image_artifact, image_artifact]))
        Agent(config=MockStructureConfig()).add_task(task)

        assert isinstance(task.image_query_engine, ImageQueryEngine)
        assert isinstance(task.image_query_engine.image_query_driver, MockImageQueryDriver)

    def test_missing_image_generation_engine(self, text_artifact, image_artifact):
        task = ImageQueryTask((text_artifact, [image_artifact, image_artifact]))

        with pytest.raises(ValueError):
            task.image_query_engine
