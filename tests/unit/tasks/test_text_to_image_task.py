from unittest.mock import Mock

from griptape.tasks import TextToImageTask


class TestTextToImageTask:
    def test_accepts_string_input(self):
        task = TextToImageTask(input="string input", image_generation_engine=Mock())

        assert task.input.value == "string input"
