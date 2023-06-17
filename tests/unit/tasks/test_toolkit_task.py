import pytest
from griptape.drivers import LocalVectorStoreDriver
from griptape.engines import VectorQueryEngine
from griptape.memory.tool import TextToolMemory
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
from tests.mocks.mock_tool.tool import MockTool
from griptape.artifacts import ErrorArtifact
from griptape.tasks import ToolkitTask, ActionSubtask
from tests.mocks.mock_value_prompt_driver import MockValuePromptDriver
from griptape.structures import Pipeline


class TestToolkitSubtask:
    @pytest.fixture
    def query_engine(self):
        return VectorQueryEngine(
            vector_store_driver=LocalVectorStoreDriver(
                embedding_driver=MockEmbeddingDriver()
            )
        )

    def test_init(self):
        assert len(ToolkitTask("test", tools=[MockTool(name="Tool1"), MockTool(name="Tool2")]).tools) == 2

        try:
            ToolkitTask("test", tools=[MockTool(), MockTool()])
            assert False
        except ValueError:
            assert True

    def test_run(self):
        output = """Output: done"""

        task = ToolkitTask("test", tools=[MockTool(name="Tool1"), MockTool(name="Tool2")])
        pipeline = Pipeline(
            prompt_driver=MockValuePromptDriver(output)
        )

        pipeline.add_task(task)

        result = pipeline.run()

        assert len(task.tools) == 2
        assert len(task._subtasks) == 1
        assert result.output.to_text() == "done"
    
    def test_run_max_subtasks(self):
        output = """Action: {"tool": "test"}"""

        task = ToolkitTask("test", tools=[MockTool(name="Tool1")], max_subtasks=3)
        pipeline = Pipeline(prompt_driver=MockValuePromptDriver(output))

        pipeline.add_task(task)

        pipeline.run()

        assert len(task._subtasks) == 3
        assert isinstance(task.output, ErrorArtifact)

    def test_init_from_prompt_1(self):
        valid_input = 'Thought: need to test\n' \
                      'Action: {"type": "tool", "name": "test", "activity": "test action", "input": "test input"}\n' \
                      'Observation: test observation\n' \
                      'Output: test output'
        task = ToolkitTask("test", tools=[MockTool(name="Tool1")])

        Pipeline().add_task(task)

        subtask = task.add_subtask(ActionSubtask(valid_input))

        assert subtask.thought == "need to test"
        assert subtask.action_type == "tool"
        assert subtask.action_name == "test"
        assert subtask.action_activity == "test action"
        assert subtask.action_input == "test input"
        assert subtask.output is None

    def test_init_from_prompt_2(self):
        valid_input = """Thought: need to test\nObservation: test 
        observation\nOutput: test output"""
        task = ToolkitTask("test", tools=[MockTool(name="Tool1")])

        Pipeline().add_task(task)

        subtask = task.add_subtask(ActionSubtask(valid_input))

        assert subtask.thought == "need to test"
        assert subtask.action_name is None
        assert subtask.action_activity is None
        assert subtask.action_input is None
        assert subtask.output.to_text() == "test output"

    def test_add_subtask(self):
        task = ToolkitTask("test", tools=[MockTool(name="Tool1")])
        subtask1 = ActionSubtask("test1", action_name="test", action_activity="test", action_input={"values": {"f": "b"}})
        subtask2 = ActionSubtask("test2", action_name="test", action_activity="test", action_input={"values": {"f": "b"}})

        Pipeline().add_task(task)

        task.add_subtask(subtask1)
        task.add_subtask(subtask2)

        assert len(task._subtasks) == 2

        assert len(subtask1.children) == 1
        assert len(subtask1.parents) == 0
        assert subtask1.children[0] == subtask2

        assert len(subtask2.children) == 0
        assert len(subtask2.parents) == 1
        assert subtask2.parents[0] == subtask1

    def test_find_subtask(self):
        task = ToolkitTask("test", tools=[MockTool(name="Tool1")])
        subtask1 = ActionSubtask("test1", action_name="test", action_activity="test", action_input={"values": {"f": "b"}})
        subtask2 = ActionSubtask("test2", action_name="test", action_activity="test", action_input={"values": {"f": "b"}})

        Pipeline().add_task(task)

        task.add_subtask(subtask1)
        task.add_subtask(subtask2)

        assert task.find_subtask(subtask1.id) == subtask1
        assert task.find_subtask(subtask2.id) == subtask2
    
    def test_find_tool(self):
        tool = MockTool()
        task = ToolkitTask("test", tools=[tool])

        Pipeline().add_task(task)

        assert task.find_tool(tool.name) == tool

    def test_find_memory(self, query_engine):
        m1 = TextToolMemory(id="Memory1", query_engine=query_engine)
        m2 = TextToolMemory(id="Memory2", query_engine=query_engine)

        tool = MockTool(
            name="Tool1",
            output_memory={
                "test": [m1, m2]
            }
        )
        task = ToolkitTask("test", tools=[tool])

        Pipeline().add_task(task)

        assert task.find_memory("Memory1") == m1
        assert task.find_memory("Memory2") == m2

    def test_memory(self, query_engine):
        tool1 = MockTool(
            name="Tool1",
            output_memory={
                "test": [
                    TextToolMemory(id="Memory1", query_engine=query_engine),
                    TextToolMemory(id="Memory2", query_engine=query_engine)
                ]
            }
        )

        tool2 = MockTool(
            name="Tool2",
            output_memory={
                "test": [
                    TextToolMemory(id="Memory2", query_engine=query_engine),
                    TextToolMemory(id="Memory3", query_engine=query_engine)
                ]
            }
        )

        task = ToolkitTask(tools=[tool1, tool2])

        Pipeline().add_task(task)

        assert len(task.memory) == 3
        assert task.memory[0].id == "Memory1"
        assert task.memory[1].id == "Memory2"
        assert task.memory[2].id == "Memory3"
