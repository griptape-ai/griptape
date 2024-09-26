import pytest

from griptape.memory import TaskMemory
from griptape.memory.structure import ConversationMemory
from griptape.memory.task.storage import TextArtifactStorage
from griptape.rules import Rule, Ruleset
from griptape.structures import Agent
from griptape.tasks import BaseTask, PromptTask, ToolkitTask
from tests.mocks.mock_prompt_driver import MockPromptDriver
from tests.mocks.mock_tool.tool import MockTool


class TestAgent:
    def test_init(self):
        driver = MockPromptDriver()
        agent = Agent(prompt_driver=driver, rulesets=[Ruleset("TestRuleset", [Rule("test")])])

        assert agent.prompt_driver is driver
        assert isinstance(agent.task, PromptTask)
        assert isinstance(agent.task, PromptTask)
        assert agent.rulesets[0].name == "TestRuleset"
        assert agent.rulesets[0].rules[0].value == "test"
        assert isinstance(agent.conversation_memory, ConversationMemory)
        assert isinstance(Agent(tools=[MockTool()]).task, ToolkitTask)

    def test_rulesets(self):
        agent = Agent(rulesets=[Ruleset("Foo", [Rule("foo test")])])

        agent.add_task(PromptTask(rulesets=[Ruleset("Bar", [Rule("bar test")])]))

        assert isinstance(agent.task, PromptTask)
        assert len(agent.task.all_rulesets) == 2
        assert agent.task.all_rulesets[0].name == "Foo"
        assert agent.task.all_rulesets[1].name == "Bar"

    def test_rules(self):
        agent = Agent(rules=[Rule("foo test")])

        agent.add_task(PromptTask(rules=[Rule("bar test")]))

        assert isinstance(agent.task, PromptTask)
        assert len(agent.task.all_rulesets) == 2
        assert agent.task.all_rulesets[0].name == "Default Ruleset"
        assert agent.task.all_rulesets[1].name == "Additional Ruleset"

    def test_rules_and_rulesets(self):
        with pytest.raises(ValueError):
            Agent(rules=[Rule("foo test")], rulesets=[Ruleset("Bar", [Rule("bar test")])])

        agent = Agent()
        with pytest.raises(ValueError):
            agent.add_task(PromptTask(rules=[Rule("foo test")], rulesets=[Ruleset("Bar", [Rule("bar test")])]))

    def test_with_task_memory(self):
        agent = Agent(tools=[MockTool(off_prompt=True)])

        assert isinstance(agent.task_memory, TaskMemory)
        assert agent.tools[0].input_memory is not None
        assert agent.tools[0].input_memory[0] == agent.task_memory
        assert agent.tools[0].output_memory is not None
        assert agent.tools[0].output_memory["test"][0] == agent.task_memory

    def test_with_task_memory_and_empty_tool_output_memory(self):
        agent = Agent(tools=[MockTool(output_memory={}, off_prompt=True)])

        assert isinstance(agent.task_memory, TaskMemory)
        assert agent.tools[0].input_memory[0] == agent.task_memory
        assert agent.tools[0].output_memory == {}

    def test_with_no_task_memory_and_empty_tool_output_memory(self):
        agent = Agent(tools=[MockTool(output_memory={})])

        assert isinstance(agent.task_memory, TaskMemory)
        assert agent.tools[0].input_memory[0] == agent.task_memory
        assert agent.tools[0].output_memory == {}

    def test_without_default_task_memory(self):
        agent = Agent(task_memory=None, tools=[MockTool()])

        assert agent.tools[0].input_memory is None
        assert agent.tools[0].output_memory is None

    def test_with_memory(self):
        agent = Agent(prompt_driver=MockPromptDriver(), conversation_memory=ConversationMemory())

        assert agent.conversation_memory is not None
        assert len(agent.conversation_memory.runs) == 0

        agent.run()
        agent.run()
        agent.run()

        assert len(agent.conversation_memory.runs) == 3

    def test_tasks_initialization(self):
        with pytest.raises(ValueError):
            Agent(tasks=[PromptTask(), PromptTask()])

        task = PromptTask()
        agent = Agent(tasks=[task])

        assert len(agent.tasks) == 1
        assert agent.tasks[0] == task

    def test_add_task(self):
        agent = Agent(prompt_driver=MockPromptDriver())

        assert len(agent.tasks) == 1

        first_task = PromptTask("test1")
        second_task = PromptTask("test2")
        agent.add_task(first_task)

        assert len(agent.tasks) == 1
        assert agent.task == first_task

        agent + second_task

        assert len(agent.tasks) == 1
        assert agent.task == second_task

    def test_custom_task(self):
        task = PromptTask()
        agent = Agent()

        agent.add_task(task)

        assert agent.task == task

    def test_add_tasks(self):
        first_task = PromptTask("test1")
        second_task = PromptTask("test2")

        agent = Agent(prompt_driver=MockPromptDriver())

        with pytest.raises(ValueError):
            agent.add_tasks(first_task, second_task)

        with pytest.raises(ValueError):
            agent + [first_task, second_task]

        with pytest.raises(ValueError):
            agent.add_tasks([first_task, second_task])

    def test_prompt_stack_without_memory(self):
        agent = Agent(prompt_driver=MockPromptDriver(), conversation_memory=None, rules=[Rule("test")])

        task1 = PromptTask("test")

        agent.add_task(task1)

        assert len(task1.prompt_stack.messages) == 2

        agent.run()

        assert len(task1.prompt_stack.messages) == 3

        agent.run()

        assert len(task1.prompt_stack.messages) == 3

    def test_prompt_stack_with_memory(self):
        agent = Agent(prompt_driver=MockPromptDriver(), conversation_memory=ConversationMemory(), rules=[Rule("test")])

        task1 = PromptTask("test")

        agent.add_task(task1)

        assert len(task1.prompt_stack.messages) == 2

        agent.run()

        assert len(task1.prompt_stack.messages) == 5

        agent.run()

        assert len(task1.prompt_stack.messages) == 7

    def test_run(self):
        task = PromptTask("test")
        agent = Agent(prompt_driver=MockPromptDriver())
        agent.add_task(task)

        assert task.state == BaseTask.State.PENDING

        result = agent.run()

        assert "mock output" in result.output_task.output.to_text()
        assert task.state == BaseTask.State.FINISHED

    def test_run_with_args(self):
        task = PromptTask("{{ args[0] }}-{{ args[1] }}")
        agent = Agent(prompt_driver=MockPromptDriver())
        agent.add_task(task)

        agent._execution_args = ("test1", "test2")

        assert task.input.to_text() == "test1-test2"

        agent.run()

        assert task.input.to_text() == "-"

    def test_context(self):
        task = PromptTask("test prompt")
        agent = Agent(prompt_driver=MockPromptDriver())

        agent.add_task(task)

        agent.run("hello")

        context = agent.context(task)

        assert context["structure"] == agent

    def test_task_memory_defaults(self, mock_config):
        agent = Agent()

        storage = list(agent.task_memory.artifact_storages.values())[0]
        assert isinstance(storage, TextArtifactStorage)

        assert storage.vector_store_driver.embedding_driver == mock_config.drivers_config.embedding_driver

    def finished_tasks(self):
        task = PromptTask("test prompt")
        agent = Agent(prompt_driver=MockPromptDriver())

        agent.add_task(task)

        agent.run("hello")

        assert len(agent.finished_tasks) == 1

    def test_fail_fast(self):
        with pytest.raises(ValueError):
            Agent(prompt_driver=MockPromptDriver(), fail_fast=True)
