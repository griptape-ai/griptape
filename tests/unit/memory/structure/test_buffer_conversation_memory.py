import json
from griptape.tasks import PromptTask
from griptape.structures import Pipeline
from griptape.memory.structure import BufferConversationMemory, Run
from tests.mocks.mock_prompt_driver import MockPromptDriver


class TestBufferConversationMemory:
    def test_after_run(self):
        memory = BufferConversationMemory(buffer_size=2)

        pipeline = Pipeline(memory=memory, prompt_driver=MockPromptDriver())

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
        memory = BufferConversationMemory()
        memory.add_run(Run(input="foo", output="bar"))

        assert json.loads(memory.to_json())["type"] == "BufferConversationMemory"
        assert json.loads(memory.to_json())["runs"][0]["input"] == "foo"

    def test_to_dict(self):
        memory = BufferConversationMemory()
        memory.add_run(Run(input="foo", output="bar"))

        assert memory.to_dict()["type"] == "BufferConversationMemory"
        assert memory.to_dict()["runs"][0]["input"] == "foo"

    def test_from_dict(self):
        memory = BufferConversationMemory()
        memory.add_run(Run(input="foo", output="bar"))
        memory_dict = memory.to_dict()

        assert isinstance(memory.from_dict(memory_dict), BufferConversationMemory)
        assert memory.from_dict(memory_dict).runs[0].input == "foo"

    def test_from_json(self):
        memory = BufferConversationMemory()
        memory.add_run(Run(input="foo", output="bar"))
        memory_dict = memory.to_dict()

        assert isinstance(memory.from_dict(memory_dict), BufferConversationMemory)
        assert memory.from_dict(memory_dict).runs[0].input == "foo"
