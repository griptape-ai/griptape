import pytest

from griptape.structures import Agent, Pipeline, Structure
from griptape.tasks import PromptTask


class TestStructure:
    def test_output(self):
        pipeline = Pipeline()
        with pytest.raises(
            ValueError, match="Structure has no output Task. Add a Task to the Structure to generate output."
        ):
            assert pipeline.output

        agent = Agent()
        with pytest.raises(
            ValueError, match="Structure's output Task has no output. Run the Structure to generate output."
        ):
            assert agent.output

    def test_conversation_mode_per_structure(self):
        pipeline = Pipeline(
            conversation_memory_strategy=Structure.ConversationMemoryStrategy.PER_STRUCTURE,
            tasks=[PromptTask("1"), PromptTask("2")],
        )

        pipeline.run()
        assert pipeline.conversation_memory is not None
        assert len(pipeline.conversation_memory.runs) == 1
        assert pipeline.conversation_memory.runs[0].input.value == "1"
        assert pipeline.conversation_memory.runs[0].output.value == "mock output"

    def test_conversation_mode_per_task(self):
        pipeline = Pipeline(
            conversation_memory_strategy=Structure.ConversationMemoryStrategy.PER_TASK,
            tasks=[PromptTask("1"), PromptTask("2")],
        )

        pipeline.run()
        assert pipeline.conversation_memory is not None
        assert len(pipeline.conversation_memory.runs) == 2
        assert pipeline.conversation_memory.runs[0].input.value == "1"
        assert pipeline.conversation_memory.runs[0].output.value == "mock output"
        assert pipeline.conversation_memory.runs[1].input.value == "2"
        assert pipeline.conversation_memory.runs[1].output.value == "mock output"

    def test_conversation_mode_per_task_no_memory(self):
        pipeline = Pipeline(
            conversation_memory_strategy=Structure.ConversationMemoryStrategy.PER_TASK,
            tasks=[PromptTask(conversation_memory=None), PromptTask("2")],
        )

        pipeline.run()
        assert pipeline.conversation_memory is not None
        assert len(pipeline.conversation_memory.runs) == 1
        assert pipeline.conversation_memory.runs[0].input.value == "2"
