import pytest

from griptape.artifacts.image_artifact import ImageArtifact
from griptape.artifacts.list_artifact import ListArtifact
from griptape.artifacts.text_artifact import TextArtifact
from griptape.memory.structure import ConversationMemory
from griptape.memory.structure.run import Run
from griptape.rules import Rule
from griptape.structures import Pipeline
from griptape.tasks import PromptTask
from tests.mocks.mock_prompt_driver import MockPromptDriver
from tests.mocks.mock_structure_config import MockStructureConfig


class TestPromptTask:
    def test_run(self):
        task = PromptTask("test")
        pipeline = Pipeline(prompt_driver=MockPromptDriver())

        pipeline.add_task(task)

        assert task.run().to_text() == "mock output"

    def test_to_text(self):
        task = PromptTask("{{ test }}", context={"test": "test value"})

        Pipeline().add_task(task)

        assert task.input.to_text() == "test value"

    def test_config_prompt_driver(self):
        task = PromptTask("test")
        Pipeline(config=MockStructureConfig()).add_task(task)

        assert isinstance(task.prompt_driver, MockPromptDriver)

    def test_missing_prompt_driver(self):
        task = PromptTask("test")

        with pytest.raises(ValueError):
            task.prompt_driver  # noqa: B018

    def test_input(self):
        # Str
        task = PromptTask("test")

        assert task.input.value == "test"

        # List of strs
        task = PromptTask(["test1", "test2"])

        assert task.input.value[0].value == "test1"
        assert task.input.value[1].value == "test2"

        # Tuple of strs
        task = PromptTask(("test1", "test2"))

        assert task.input.value[0].value == "test1"
        assert task.input.value[1].value == "test2"

        # Image artifact
        task = PromptTask(ImageArtifact(b"image-data", format="png", width=100, height=100))

        assert isinstance(task.input, ImageArtifact)
        assert task.input.value == b"image-data"
        assert task.input.format == "png"
        assert task.input.width == 100
        assert task.input.height == 100

        # List of str and image artifact
        task = PromptTask(["foo", ImageArtifact(b"image-data", format="png", width=100, height=100)])

        assert isinstance(task.input, ListArtifact)
        assert task.input.value[0].value == "foo"
        assert isinstance(task.input.value[1], ImageArtifact)
        assert task.input.value[1].value == b"image-data"
        assert task.input.value[1].format == "png"
        assert task.input.value[1].width == 100

        # List of str and nested image artifact
        task = PromptTask(["foo", [ImageArtifact(b"image-data", format="png", width=100, height=100)]])
        assert isinstance(task.input, ListArtifact)
        assert task.input.value[0].value == "foo"
        assert isinstance(task.input.value[1], ListArtifact)
        assert isinstance(task.input.value[1].value[0], ImageArtifact)
        assert task.input.value[1].value[0].value == b"image-data"
        assert task.input.value[1].value[0].format == "png"
        assert task.input.value[1].value[0].width == 100

        # Tuple of str and image artifact
        task = PromptTask(("foo", ImageArtifact(b"image-data", format="png", width=100, height=100)))

        assert isinstance(task.input, ListArtifact)
        assert task.input.value[0].value == "foo"
        assert isinstance(task.input.value[1], ImageArtifact)
        assert task.input.value[1].value == b"image-data"
        assert task.input.value[1].format == "png"
        assert task.input.value[1].width == 100

        # Lambda returning list of str and image artifact
        task = PromptTask(
            ListArtifact([TextArtifact("foo"), ImageArtifact(b"image-data", format="png", width=100, height=100)])
        )

        assert isinstance(task.input, ListArtifact)
        assert task.input.value[0].value == "foo"
        assert isinstance(task.input.value[1], ImageArtifact)
        assert task.input.value[1].value == b"image-data"
        assert task.input.value[1].format == "png"
        assert task.input.value[1].width == 100

        # Lambda returning list of str and image artifact
        task = PromptTask(
            lambda _: ListArtifact(
                [TextArtifact("foo"), ImageArtifact(b"image-data", format="png", width=100, height=100)]
            )
        )
        assert isinstance(task.input, ListArtifact)
        assert task.input.value[0].value == "foo"
        assert isinstance(task.input.value[1], ImageArtifact)
        assert task.input.value[1].value == b"image-data"
        assert task.input.value[1].format == "png"
        assert task.input.value[1].width == 100

        # default case
        task = PromptTask({"default": "test"})

        assert task.input.value == str({"default": "test"})

    def test_prompt_stack(self):
        task = PromptTask("{{ test }}", context={"test": "test value"}, rules=[Rule("test rule")])

        Pipeline().add_task(task)

        assert len(task.prompt_stack.messages) == 2
        assert task.prompt_stack.messages[0].is_system()
        assert task.prompt_stack.messages[1].is_user()

    def test_prompt_stack_empty_system_content(self):
        task = PromptTask("{{ test }}", context={"test": "test value"})

        pipeline = Pipeline(
            conversation_memory=ConversationMemory(
                runs=[Run(input=TextArtifact("input"), output=TextArtifact("output"))]
            )
        )
        pipeline.add_task(task)

        assert len(task.prompt_stack.messages) == 3
        assert task.prompt_stack.messages[0].is_user()
        assert task.prompt_stack.messages[0].to_text() == "input"
        assert task.prompt_stack.messages[1].is_assistant()
        assert task.prompt_stack.messages[1].to_text() == "output"
        assert task.prompt_stack.messages[2].is_user()
        assert task.prompt_stack.messages[2].to_text() == "test value"
