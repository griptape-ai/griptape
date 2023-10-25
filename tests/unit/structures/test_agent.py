import pytest
from griptape.memory.structure import ConversationMemory
from griptape.memory import ToolMemory
from griptape.memory.tool.storage import TextArtifactStorage
from griptape.rules import Rule, Ruleset
from griptape.structures import Agent
from griptape.tasks import PromptTask, BaseTask, ToolkitTask
from tests.mocks.mock_prompt_driver import MockPromptDriver
from tests.mocks.mock_tool.tool import MockTool
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver


class TestAgent:
    def test_init(self):
        driver = MockPromptDriver()
        agent = Agent(
            prompt_driver=driver,
            rulesets=[Ruleset("TestRuleset", [Rule("test")])],
        )

        assert agent.prompt_driver is driver
        assert isinstance(agent.task, PromptTask)
        assert isinstance(agent.task, PromptTask)
        assert agent.rulesets[0].name is "TestRuleset"
        assert agent.rulesets[0].rules[0].value is "test"
        assert isinstance(agent.memory, ConversationMemory)
        assert isinstance(Agent(tools=[MockTool()]).task, ToolkitTask)

    def test_rulesets(self):
        agent = Agent(rulesets=[Ruleset("Foo", [Rule("foo test")])])

        agent.add_task(
            PromptTask(rulesets=[Ruleset("Bar", [Rule("bar test")])])
        )

        assert len(agent.task.all_rulesets) == 2
        assert agent.task.all_rulesets[0].name == "Foo"
        assert agent.task.all_rulesets[1].name == "Bar"

    def test_rules(self):
        agent = Agent(rules=[Rule("foo test")])

        agent.add_task(PromptTask(rules=[Rule("bar test")]))

        assert len(agent.task.all_rulesets) == 2
        assert agent.task.all_rulesets[0].name == "Default Ruleset"
        assert agent.task.all_rulesets[1].name == "Additional Ruleset"

    def test_rules_and_rulesets(self):
        with pytest.raises(ValueError):
            Agent(
                rules=[Rule("foo test")],
                rulesets=[Ruleset("Bar", [Rule("bar test")])],
            )

        with pytest.raises(ValueError):
            agent = Agent()
            agent.add_task(
                PromptTask(
                    rules=[Rule("foo test")],
                    rulesets=[Ruleset("Bar", [Rule("bar test")])],
                )
            )

    def test_with_default_tool_memory(self):
        agent = Agent(tools=[MockTool()])

        assert isinstance(agent.tool_memory, ToolMemory)
        assert agent.tools[0].input_memory[0] == agent.tool_memory
        assert agent.tools[0].output_memory["test"][0] == agent.tool_memory
        assert (
            agent.tools[0].output_memory.get("test_without_default_memory")
            is None
        )

    def test_with_default_tool_memory_and_empty_tool_output_memory(self):
        agent = Agent(tools=[MockTool(output_memory={})])

        assert agent.tools[0].output_memory == {}

    def test_embedding_driver(self):
        embedding_driver = MockEmbeddingDriver()
        agent = Agent(tools=[MockTool()], embedding_driver=embedding_driver)

        memory_embedding_driver = list(
            agent.tool_memory.artifact_storages.values()
        )[0].query_engine.vector_store_driver.embedding_driver

        assert memory_embedding_driver == embedding_driver

    def test_without_default_tool_memory(self):
        agent = Agent(tool_memory=None, tools=[MockTool()])

        assert agent.tools[0].input_memory is None
        assert agent.tools[0].output_memory is None

    def test_with_memory(self):
        agent = Agent(
            prompt_driver=MockPromptDriver(), memory=ConversationMemory()
        )

        assert agent.memory is not None
        assert len(agent.memory.runs) == 0

        agent.run()
        agent.run()
        agent.run()

        assert len(agent.memory.runs) == 3

    def test_tasks_validation(self):
        with pytest.raises(ValueError):
            Agent(tasks=[PromptTask()])

    def test_add_task(self):
        first_task = PromptTask("test1")
        second_task = PromptTask("test2")

        agent = Agent(prompt_driver=MockPromptDriver())

        assert len(agent.tasks) == 1

        agent.add_task(first_task)

        assert len(agent.tasks) == 1
        assert agent.task == first_task

        agent.add_task(second_task)

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

        try:
            agent.add_tasks(first_task, second_task)
            assert False
        except NotImplementedError:
            assert True

    def test_prompt_stack_without_memory(self):
        agent = Agent(prompt_driver=MockPromptDriver(), memory=None)

        task1 = PromptTask("test")

        agent.add_task(task1)

        assert len(task1.prompt_stack.inputs) == 2

        agent.run()

        assert len(task1.prompt_stack.inputs) == 3

        agent.run()

        assert len(task1.prompt_stack.inputs) == 3

    def test_prompt_stack_with_memory(self):
        agent = Agent(
            prompt_driver=MockPromptDriver(), memory=ConversationMemory()
        )

        task1 = PromptTask("test")

        agent.add_task(task1)

        assert len(task1.prompt_stack.inputs) == 2

        agent.run()

        assert len(task1.prompt_stack.inputs) == 5

        agent.run()

        assert len(task1.prompt_stack.inputs) == 7

    def test_run(self):
        task = PromptTask("test")
        agent = Agent(prompt_driver=MockPromptDriver())
        agent.add_task(task)

        assert task.state == BaseTask.State.PENDING

        result = agent.run()

        assert "mock output" in result.output.to_text()
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

    def test_tool_memory_defaults(self):
        prompt_driver = MockPromptDriver()
        embedding_driver = MockEmbeddingDriver()
        agent = Agent(
            prompt_driver=prompt_driver, embedding_driver=embedding_driver
        )

        storage: TextArtifactStorage = list(
            agent.tool_memory.artifact_storages.values()
        )[0]

        assert storage.query_engine.prompt_driver == prompt_driver
        assert (
            storage.query_engine.vector_store_driver.embedding_driver
            == embedding_driver
        )
        assert storage.summary_engine.prompt_driver == prompt_driver
        assert storage.csv_extraction_engine.prompt_driver == prompt_driver
        assert storage.json_extraction_engine.prompt_driver == prompt_driver
