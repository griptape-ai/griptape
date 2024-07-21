from unittest.mock import Mock

import pytest

from griptape.artifacts import ImageArtifact, TextArtifact
from griptape.artifacts.list_artifact import ListArtifact
from griptape.engines import VariationImageGenerationEngine
from griptape.structures import Agent
from griptape.tasks import BaseTask, VariationImageGenerationTask
from tests.mocks.mock_image_generation_driver import MockImageGenerationDriver
from tests.mocks.mock_structure_config import MockStructureConfig


class TestVariationImageGenerationTask:
    @pytest.fixture()
    def text_artifact(self):
        return TextArtifact(value="some text")

    @pytest.fixture()
    def image_artifact(self):
        return ImageArtifact(value=b"some image data", format="png", width=512, height=512)

    def test_artifact_inputs(self, text_artifact: TextArtifact, image_artifact: ImageArtifact):
        input_tuple = (text_artifact, image_artifact)
        task = VariationImageGenerationTask(input_tuple, image_generation_engine=Mock())

        assert task.input.value == list(input_tuple)

    def test_callable_input(self, text_artifact: TextArtifact, image_artifact: ImageArtifact):
        artifacts = [text_artifact, image_artifact]

        def callable_input(task: BaseTask) -> ListArtifact:
            return ListArtifact(artifacts)

        task = VariationImageGenerationTask(callable_input, image_generation_engine=Mock())

        assert task.input.value == artifacts

    def test_list_input(self, text_artifact: TextArtifact, image_artifact: ImageArtifact):
        artifact_input = [text_artifact, image_artifact]
        task = VariationImageGenerationTask(ListArtifact(artifact_input), image_generation_engine=Mock())

        assert task.input.value == artifact_input

    def test_bad_input(self, image_artifact):
        with pytest.raises(ValueError):
            VariationImageGenerationTask(("foo", "bar")).run()  # pyright: ignore[reportArgumentType]

    def test_config_image_generation_engine(self, text_artifact, image_artifact):
        task = VariationImageGenerationTask((text_artifact, image_artifact))
        Agent(config=MockStructureConfig()).add_task(task)

        assert isinstance(task.image_generation_engine, VariationImageGenerationEngine)
        assert isinstance(task.image_generation_engine.image_generation_driver, MockImageGenerationDriver)

    def test_missing_summary_engine(self, text_artifact, image_artifact):
        task = VariationImageGenerationTask((text_artifact, image_artifact))

        with pytest.raises(ValueError):
            task.image_generation_engine  # noqa: B018
