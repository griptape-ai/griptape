import pytest

from griptape.structures import Agent, Pipeline
from griptape.tasks import PromptTask
from tests.mocks.mock_prompt_driver import MockPromptDriver


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

    def test_to_dict(self):
        task = PromptTask("test prompt")
        agent = Agent(prompt_driver=MockPromptDriver())
        agent.add_task(task)
        expected_agent_dict = {
            "type": "Agent",
            "id": agent.id,
            "tasks": [
                {
                    "type": agent.tasks[0].type,
                    "id": agent.tasks[0].id,
                    "state": str(agent.tasks[0].state),
                    "parent_ids": agent.tasks[0].parent_ids,
                    "child_ids": agent.tasks[0].child_ids,
                    "max_meta_memory_entries": agent.tasks[0].max_meta_memory_entries,
                    "context": agent.tasks[0].context,
                }
            ],
            "conversation_memory": {
                "type": agent.conversation_memory.type,
                "runs": agent.conversation_memory.runs,
                "meta": agent.conversation_memory.meta,
                "max_runs": agent.conversation_memory.max_runs,
            },
            "conversation_memory_strategy": agent.conversation_memory_strategy,
        }
        assert agent.to_dict() == expected_agent_dict

        agent.run()

        expected_agent_dict = {
            **expected_agent_dict,
            "tasks": [
                {
                    **expected_agent_dict["tasks"][0],
                    "state": str(agent.tasks[0].state),
                }
            ],
            "conversation_memory": {
                **expected_agent_dict["conversation_memory"],
                "runs": agent.conversation_memory.to_dict()["runs"],
            },
        }
        assert agent.to_dict() == expected_agent_dict

    def test_from_dict(self):
        task = PromptTask("test prompt")
        agent = Agent(prompt_driver=MockPromptDriver())
        agent.add_task(task)

        serialized_agent = agent.to_dict()
        assert isinstance(serialized_agent, dict)

        deserialized_agent = Agent.from_dict(serialized_agent)
        assert isinstance(deserialized_agent, Agent)

        assert deserialized_agent.task_outputs[task.id] is None
        deserialized_agent.run()

        assert len(deserialized_agent.task_outputs) == 1
        assert deserialized_agent.task_outputs[task.id].value == "mock output"
