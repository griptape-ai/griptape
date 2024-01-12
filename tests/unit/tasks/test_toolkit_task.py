import pytest
from griptape.artifacts import ErrorArtifact, TextArtifact
from griptape.drivers import LocalVectorStoreDriver
from griptape.engines import VectorQueryEngine
from griptape.structures import Agent
from griptape.tasks import ToolkitTask, ActionSubtask
from griptape.utils import PromptStack
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
from tests.mocks.mock_prompt_driver import MockPromptDriver
from tests.mocks.mock_tool.tool import MockTool
from tests.mocks.mock_value_prompt_driver import MockValuePromptDriver
from tests.utils import defaults


class TestToolkitSubtask:
    @pytest.fixture
    def query_engine(self):
        return VectorQueryEngine(
            prompt_driver=MockPromptDriver(),
            vector_store_driver=LocalVectorStoreDriver(embedding_driver=MockEmbeddingDriver()),
        )

    def test_init(self):
        assert len(ToolkitTask("test", tools=[MockTool(name="Tool1"), MockTool(name="Tool2")]).tools) == 2

        try:
            ToolkitTask("test", tools=[MockTool(), MockTool()])
            assert False
        except ValueError:
            assert True

    def test_run(self):
        output = """Answer: done"""

        task = ToolkitTask("test", tools=[MockTool(name="Tool1"), MockTool(name="Tool2")])
        agent = Agent(prompt_driver=MockValuePromptDriver(output))

        agent.add_task(task)

        result = agent.run()

        assert len(task.tools) == 2
        assert len(task.subtasks) == 1
        assert result.output_task.output.to_text() == "done"

    def test_run_max_subtasks(self):
        output = """Action: {"name": "blah"}"""

        task = ToolkitTask("test", tools=[MockTool(name="Tool1")], max_subtasks=3)
        agent = Agent(prompt_driver=MockValuePromptDriver(output))

        agent.add_task(task)

        agent.run()

        assert len(task.subtasks) == 3
        assert isinstance(task.output, ErrorArtifact)

    def test_run_invalid_react_prompt(self):
        output = """foo bar"""

        task = ToolkitTask("test", tools=[MockTool(name="Tool1")], max_subtasks=3)
        agent = Agent(prompt_driver=MockValuePromptDriver(output))

        agent.add_task(task)

        result = agent.run()

        assert len(task.subtasks) == 1
        assert result.output_task.output.to_text() == "foo bar"

    def test_init_from_prompt_1(self):
        valid_input = (
            "Thought: need to test\n"
            'Action: {"name": "test", "path": "test action", "input": "test input"}\n'
            "<|Response|>: test observation\n"
            "Answer: test output"
        )
        task = ToolkitTask("test", tools=[MockTool(name="Tool1")])

        Agent().add_task(task)

        subtask = task.add_subtask(ActionSubtask(valid_input))

        assert subtask.thought == "need to test"
        assert subtask.action_name == "test"
        assert subtask.action_path == "test action"
        assert subtask.action_input == "test input"
        assert subtask.output is None

    def test_init_from_prompt_2(self):
        valid_input = """Thought: need to test\nObservation: test 
        observation\nAnswer: test output"""
        task = ToolkitTask("test", tools=[MockTool(name="Tool1")])

        Agent().add_task(task)

        subtask = task.add_subtask(ActionSubtask(valid_input))

        assert subtask.thought == "need to test"
        assert subtask.action_name is None
        assert subtask.action_path is None
        assert subtask.action_input is None
        assert subtask.output.to_text() == "test output"

    def test_add_subtask(self):
        task = ToolkitTask("test", tools=[MockTool(name="Tool1")])
        subtask1 = ActionSubtask("test1", action_name="test", action_path="test", action_input={"values": {"f": "b"}})
        subtask2 = ActionSubtask("test2", action_name="test", action_path="test", action_input={"values": {"f": "b"}})

        Agent().add_task(task)

        task.add_subtask(subtask1)
        task.add_subtask(subtask2)

        assert len(task.subtasks) == 2

        assert len(subtask1.children) == 1
        assert len(subtask1.parents) == 0
        assert subtask1.children[0] == subtask2

        assert len(subtask2.children) == 0
        assert len(subtask2.parents) == 1
        assert subtask2.parents[0] == subtask1

    def test_find_subtask(self):
        task = ToolkitTask("test", tools=[MockTool(name="Tool1")])
        subtask1 = ActionSubtask("test1", action_name="test", action_path="test", action_input={"values": {"f": "b"}})
        subtask2 = ActionSubtask("test2", action_name="test", action_path="test", action_input={"values": {"f": "b"}})

        Agent().add_task(task)

        task.add_subtask(subtask1)
        task.add_subtask(subtask2)

        assert task.find_subtask(subtask1.id) == subtask1
        assert task.find_subtask(subtask2.id) == subtask2

    def test_find_tool(self):
        tool = MockTool()
        task = ToolkitTask("test", tools=[tool])

        Agent().add_task(task)

        assert task.find_tool(tool.name) == tool

    def test_find_memory(self, query_engine):
        m1 = defaults.text_task_memory("Memory1")
        m2 = defaults.text_task_memory("Memory2")

        tool = MockTool(name="Tool1", output_memory={"test": [m1, m2]})
        task = ToolkitTask("test", tools=[tool])

        Agent().add_task(task)

        assert task.find_memory("Memory1") == m1
        assert task.find_memory("Memory2") == m2

    def test_memory(self, query_engine):
        tool1 = MockTool(
            name="Tool1",
            output_memory={"test": [defaults.text_task_memory("Memory1"), defaults.text_task_memory("Memory2")]},
        )

        tool2 = MockTool(
            name="Tool2",
            output_memory={"test": [defaults.text_task_memory("Memory1"), defaults.text_task_memory("Memory3")]},
        )

        task = ToolkitTask(tools=[tool1, tool2])

        Agent().add_task(task)

        assert len(task.tool_output_memory) == 3
        assert task.tool_output_memory[0].name == "Memory1"
        assert task.tool_output_memory[1].name == "Memory2"
        assert task.tool_output_memory[2].name == "Memory3"

    def test_meta_memory(self):
        memory = defaults.text_task_memory("TestMemory")
        subtask = ActionSubtask()
        agent = Agent(task_memory=memory)

        subtask.structure = agent

        memory.process_output(MockTool().test, subtask, TextArtifact("foo"))

        task = ToolkitTask(tools=[MockTool()])

        agent.add_task(task)

        system_template = task.generate_system_template(PromptStack())

        assert "You have access to additional contextual information" in system_template
