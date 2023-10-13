from griptape.tasks import PromptTask
from tests.mocks.mock_prompt_driver import MockPromptDriver
from griptape.structures import Pipeline


class TestPromptSubtask:
    def test_run(self):
        task = PromptTask("test")
        pipeline = Pipeline(prompt_driver=MockPromptDriver())

        pipeline.add_task(task)

        assert task.run().to_text() == "mock output"

    def test_to_text(self):
        task = PromptTask("{{ test }}", context={"test": "test value"})

        Pipeline().add_task(task)

        assert task.input.to_text() == "test value"

    def test_to_dict(self):
        pipeline = Pipeline()

        task1 = PromptTask("{{ test }}", context={"test": "test value"})
        pipeline.add_task(task1)

        task2 = PromptTask()
        pipeline.add_task(task2)

        assert task1.to_dict() == {
            "id": task1.id,
            "state": 1,
            "parent_ids": [],
            "child_ids": [task2.id],
            "output": None,
            "input": {
                "id": task1.input.id,
                "name": task1.input.name,
                "type": "TextArtifact",
                "value": "test value",
            },
            "input_template": "{{ test }}",
            "context": {"test": "test value"},
        }

        assert task2.to_dict() == {
            "id": task2.id,
            "state": 1,
            "parent_ids": [task1.id],
            "child_ids": [],
            "output": None,
            "input": {"id": task2.input.id, "name": task2.input.name, "type": "TextArtifact", "value": ""},
            "input_template": "{{ args[0] }}",
            "context": {},
        }
