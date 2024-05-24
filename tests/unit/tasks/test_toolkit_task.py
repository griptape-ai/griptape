import pytest
from griptape.artifacts import ErrorArtifact, TextArtifact, ActionArtifact
from griptape.drivers import LocalVectorStoreDriver
from griptape.engines import VectorQueryEngine
from griptape.structures import Agent
from griptape.tasks import ToolkitTask, ActionsSubtask, PromptTask
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
from tests.mocks.mock_prompt_driver import MockPromptDriver
from tests.mocks.mock_tool.tool import MockTool
from tests.mocks.mock_value_prompt_driver import MockValuePromptDriver
from tests.utils import defaults


class TestToolkitSubtask:
    TARGET_TOOLS_SCHEMA = {
        "description": "JSON schema for an array of actions.",
        "type": "array",
        "items": {
            "anyOf": [
                {
                    "type": "object",
                    "properties": {
                        "name": {"const": "MockTool"},
                        "path": {"description": "test description: foo", "const": "test"},
                        "input": {
                            "type": "object",
                            "properties": {
                                "values": {
                                    "description": "Test input",
                                    "type": "object",
                                    "properties": {"test": {"type": "string"}},
                                    "required": ["test"],
                                    "additionalProperties": False,
                                }
                            },
                            "required": ["values"],
                            "additionalProperties": False,
                        },
                        "tag": {"description": "Unique tag name for action execution.", "type": "string"},
                    },
                    "required": ["name", "path", "input", "tag"],
                    "additionalProperties": False,
                },
                {
                    "type": "object",
                    "properties": {
                        "name": {"const": "MockTool"},
                        "path": {"description": "test description: foo", "const": "test_error"},
                        "input": {
                            "type": "object",
                            "properties": {
                                "values": {
                                    "description": "Test input",
                                    "type": "object",
                                    "properties": {"test": {"type": "string"}},
                                    "required": ["test"],
                                    "additionalProperties": False,
                                }
                            },
                            "required": ["values"],
                            "additionalProperties": False,
                        },
                        "tag": {"description": "Unique tag name for action execution.", "type": "string"},
                    },
                    "required": ["name", "path", "input", "tag"],
                    "additionalProperties": False,
                },
                {
                    "type": "object",
                    "properties": {
                        "name": {"const": "MockTool"},
                        "path": {"description": "test description", "const": "test_list_output"},
                        "tag": {"description": "Unique tag name for action execution.", "type": "string"},
                    },
                    "required": ["name", "path", "tag"],
                    "additionalProperties": False,
                },
                {
                    "type": "object",
                    "properties": {
                        "name": {"const": "MockTool"},
                        "path": {"description": "test description", "const": "test_no_schema"},
                        "tag": {"description": "Unique tag name for action execution.", "type": "string"},
                    },
                    "required": ["name", "path", "tag"],
                    "additionalProperties": False,
                },
                {
                    "type": "object",
                    "properties": {
                        "name": {"const": "MockTool"},
                        "path": {"description": "test description: foo", "const": "test_str_output"},
                        "input": {
                            "type": "object",
                            "properties": {
                                "values": {
                                    "description": "Test input",
                                    "type": "object",
                                    "properties": {"test": {"type": "string"}},
                                    "required": ["test"],
                                    "additionalProperties": False,
                                }
                            },
                            "required": ["values"],
                            "additionalProperties": False,
                        },
                        "tag": {"description": "Unique tag name for action execution.", "type": "string"},
                    },
                    "required": ["name", "path", "input", "tag"],
                    "additionalProperties": False,
                },
                {
                    "type": "object",
                    "properties": {
                        "name": {"const": "MockTool"},
                        "path": {"description": "test description", "const": "test_without_default_memory"},
                        "input": {
                            "type": "object",
                            "properties": {
                                "values": {
                                    "description": "Test input",
                                    "type": "object",
                                    "properties": {"test": {"type": "string"}},
                                    "required": ["test"],
                                    "additionalProperties": False,
                                }
                            },
                            "required": ["values"],
                            "additionalProperties": False,
                        },
                        "tag": {"description": "Unique tag name for action execution.", "type": "string"},
                    },
                    "required": ["name", "path", "input", "tag"],
                    "additionalProperties": False,
                },
            ]
        },
        "$id": "Actions Schema",
        "$schema": "http://json-schema.org/draft-07/schema#",
    }

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
        agent = Agent(prompt_driver=MockValuePromptDriver(value=output))

        agent.add_task(task)

        result = agent.run()

        assert len(task.tools) == 2
        assert len(task.subtasks) == 1
        assert result.output_task.output.to_text() == "done"

    def test_run_max_subtasks(self):
        output = """Actions: [{"name": "blah"}]"""

        task = ToolkitTask("test", tools=[MockTool(name="Tool1")], max_subtasks=3)
        agent = Agent(prompt_driver=MockValuePromptDriver(value=output))

        agent.add_task(task)

        agent.run()

        assert len(task.subtasks) == 3
        assert isinstance(task.output, ErrorArtifact)

    def test_run_invalid_react_prompt(self):
        output = """foo bar"""

        task = ToolkitTask("test", tools=[MockTool(name="Tool1")], max_subtasks=3)
        agent = Agent(prompt_driver=MockValuePromptDriver(value=output))

        agent.add_task(task)

        result = agent.run()

        assert len(task.subtasks) == 1
        assert result.output_task.output.to_text() == "foo bar"

    def test_init_from_prompt_1(self):
        valid_input = (
            "Thought: need to test\n"
            'Actions: [{"tag": "foo", "name": "Tool1", "path": "test", "input": {"values": {"test": "value"}}}]\n'
            "<|Response|>: test observation\n"
            "Answer: test output"
        )
        task = ToolkitTask("test", tools=[MockTool(name="Tool1")])

        Agent().add_task(task)

        subtask = task.add_subtask(ActionsSubtask(valid_input))

        assert subtask.thought == "need to test"
        assert subtask.actions[0].tag == "foo"
        assert subtask.actions[0].name == "Tool1"
        assert subtask.actions[0].path == "test"
        assert subtask.actions[0].input == {"values": {"test": "value"}}
        assert subtask.output is None

    def test_init_from_prompt_2(self):
        valid_input = """Thought: need to test\nObservation: test 
        observation\nAnswer: test output"""
        task = ToolkitTask("test", tools=[MockTool(name="Tool1")])

        Agent().add_task(task)

        subtask = task.add_subtask(ActionsSubtask(valid_input))

        assert subtask.thought == "need to test"
        assert subtask.actions == []
        assert subtask.output.to_text() == "test output"

    def test_add_subtask(self):
        task = ToolkitTask("test", tools=[MockTool(name="Tool1")])
        subtask1 = ActionsSubtask(
            "test1", actions=[ActionArtifact.Action(tag="foo", name="test", path="test", input={"values": {"f": "b"}})]
        )
        subtask2 = ActionsSubtask(
            "test2", actions=[ActionArtifact.Action(tag="foo", name="test", path="test", input={"values": {"f": "b"}})]
        )

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
        subtask1 = ActionsSubtask(
            "test1", actions=[ActionArtifact.Action(tag="foo", name="test", path="test", input={"values": {"f": "b"}})]
        )
        subtask2 = ActionsSubtask(
            "test2", actions=[ActionArtifact.Action(tag="foo", name="test", path="test", input={"values": {"f": "b"}})]
        )

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
        subtask = ActionsSubtask()
        agent = Agent(task_memory=memory)

        subtask.structure = agent

        memory.process_output(MockTool().test, subtask, TextArtifact("foo"))

        task = ToolkitTask(tools=[MockTool()])

        agent.add_task(task)

        system_template = task.generate_system_template(PromptTask())

        assert "You have access to additional contextual information" in system_template

    def test_actions_schema(self):
        tool = MockTool()
        task = ToolkitTask("test", tools=[tool])

        Agent().add_task(task)

        assert task.actions_schema().json_schema("Actions Schema") == self.TARGET_TOOLS_SCHEMA
