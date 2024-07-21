from unittest.mock import Mock

import pytest

from griptape.artifacts import ImageArtifact, TextArtifact
from griptape.artifacts.list_artifact import ListArtifact
from griptape.engines import ImageQueryEngine
from griptape.structures import Agent
from griptape.tasks import BaseTask, ImageQueryTask
from tests.mocks.mock_image_query_driver import MockImageQueryDriver
from tests.mocks.mock_structure_config import MockStructureConfig


class TestImageQueryTask:
    @pytest.fixture()
    def image_query_engine(self) -> Mock:
        mock = Mock()
        mock.run.return_value = TextArtifact("image")

        return mock

    @pytest.fixture()
    def text_artifact(self):
        return TextArtifact(value="some text")

    @pytest.fixture()
    def image_artifact(self):
        return ImageArtifact(value=b"some image data", format="png", width=512, height=512)

    def test_text_inputs(self, text_artifact: TextArtifact, image_artifact: ImageArtifact):
        task = ImageQueryTask((text_artifact.value, [image_artifact, image_artifact]))

        assert task.input.value[0].value == text_artifact.value
        assert task.input.value[1] == image_artifact
        assert task.input.value[2] == image_artifact

    def test_artifact_inputs(self, text_artifact: TextArtifact, image_artifact: ImageArtifact):
        input_tuple = (text_artifact, [image_artifact, image_artifact])
        task = ImageQueryTask(input_tuple)

        assert task.input.value[0] == text_artifact
        assert task.input.value[1] == image_artifact
        assert task.input.value[2] == image_artifact

    def test_callable_input(self, text_artifact: TextArtifact, image_artifact: ImageArtifact):
        artifacts = [text_artifact, image_artifact, image_artifact]

        def callable_input(task: BaseTask) -> ListArtifact:
            return ListArtifact(value=artifacts)

        task = ImageQueryTask(callable_input)

        assert task.input.value == artifacts

    def test_list_input(self, text_artifact: TextArtifact, image_artifact: ImageArtifact):
        artifacts = [text_artifact, image_artifact, image_artifact]

        task = ImageQueryTask(ListArtifact(value=artifacts))

        assert task.input.value == artifacts

    def test_config_image_generation_engine(self, text_artifact, image_artifact):
        task = ImageQueryTask((text_artifact, [image_artifact, image_artifact]))
        Agent(config=MockStructureConfig()).add_task(task)

        assert isinstance(task.image_query_engine, ImageQueryEngine)
        assert isinstance(task.image_query_engine.image_query_driver, MockImageQueryDriver)

    def test_missing_image_generation_engine(self, text_artifact, image_artifact):
        task = ImageQueryTask((text_artifact, [image_artifact, image_artifact]))

        with pytest.raises(ValueError, match="Image Query Engine"):
            task.image_query_engine  # noqa: B018

    def test_run(self, image_query_engine, text_artifact, image_artifact):
        task = ImageQueryTask((text_artifact, [image_artifact, image_artifact]), image_query_engine=image_query_engine)
        task.run()

        assert task.output.value == "image"

    def test_bad_run(self, image_query_engine, text_artifact, image_artifact):
        with pytest.raises(ValueError, match="All inputs"):
            ImageQueryTask(("foo", [image_artifact, text_artifact]), image_query_engine=image_query_engine).run()
