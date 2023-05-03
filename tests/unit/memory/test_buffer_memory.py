import json

from griptape.tasks import PromptTask
from griptape.structures import Pipeline
from griptape.memory import BufferMemory, Run
from tests.mocks.mock_driver import MockDriver


class TestBufferMemory:
    def test_after_run(self):
        memory = BufferMemory(buffer_size=2)

        pipeline = Pipeline(memory=memory, prompt_driver=MockDriver())

        pipeline.add_tasks(
            PromptTask("test"),
            PromptTask("test"),
            PromptTask("test"),
            PromptTask("test")
        )

        pipeline.run()
        pipeline.run()

        assert len(pipeline.memory.runs) == 2

    def test_to_json(self):
        memory = BufferMemory()
        memory.add_run(Run(input="foo", output="bar"))

        assert json.loads(memory.to_json())["type"] == "BufferMemory"
        assert json.loads(memory.to_json())["runs"][0]["input"] == "foo"

    def test_to_dict(self):
        memory = BufferMemory()
        memory.add_run(Run(input="foo", output="bar"))

        assert memory.to_dict()["type"] == "BufferMemory"
        assert memory.to_dict()["runs"][0]["input"] == "foo"

    def test_from_dict(self):
        memory = BufferMemory()
        memory.add_run(Run(input="foo", output="bar"))
        memory_dict = memory.to_dict()

        assert isinstance(memory.from_dict(memory_dict), BufferMemory)
        assert memory.from_dict(memory_dict).runs[0].input == "foo"

    def test_from_json(self):
        memory = BufferMemory()
        memory.add_run(Run(input="foo", output="bar"))
        memory_dict = memory.to_dict()

        assert isinstance(memory.from_dict(memory_dict), BufferMemory)
        assert memory.from_dict(memory_dict).runs[0].input == "foo"
