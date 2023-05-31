from griptape.memory.structure import ConversationMemory
from griptape.rules import Rule, Ruleset
from griptape.structures import Agent
from griptape.tasks import PromptTask, BaseTask
from tests.mocks.mock_prompt_driver import MockPromptDriver


class TestAgent:
    def test_constructor(self):
        driver = MockPromptDriver()
        agent = Agent(prompt_driver=driver, rulesets=[Ruleset("TestRuleset", [Rule("test")])])

        assert agent.prompt_driver is driver
        assert isinstance(agent.task, PromptTask)
        assert agent.rulesets[0].name is "TestRuleset"
        assert agent.rulesets[0].rules[0].value is "test"
        assert agent.memory is None

    def test_with_memory(self):
        agent = Agent(
            prompt_driver=MockPromptDriver(),
            memory=ConversationMemory()
        )

        assert agent.memory is not None
        assert len(agent.memory.runs) == 0

        agent.run()
        agent.run()
        agent.run()

        assert len(agent.memory.runs) == 3

    def test_add_task(self):
        first_task = PromptTask("test1")
        second_task = PromptTask("test2")

        agent = Agent(
            prompt_driver=MockPromptDriver()
        )

        assert len(agent.tasks) == 1

        agent.add_task(first_task)

        assert len(agent.tasks) == 1
        assert agent.task == first_task

        agent.add_task(second_task)

        assert len(agent.tasks) == 1
        assert agent.task == second_task

    def test_add_tasks(self):
        first_task = PromptTask("test1")
        second_task = PromptTask("test2")

        agent = Agent(
            prompt_driver=MockPromptDriver()
        )

        try:
            agent.add_tasks(first_task, second_task)
            assert False
        except NotImplementedError:
            assert True

    def test_prompt_stack_without_memory(self):
        agent = Agent(
            prompt_driver=MockPromptDriver()
        )

        task1 = PromptTask("test")

        agent.add_task(task1)

        # context and first input
        assert len(agent.prompt_stack(task1)) == 2

        agent.run()

        assert len(agent.prompt_stack(task1)) == 2

    def test_prompt_stack_with_memory(self):
        agent = Agent(
            prompt_driver=MockPromptDriver(),
            memory=ConversationMemory()
        )

        task1 = PromptTask("test")
        task2 = PromptTask("test")

        agent.add_task(task1)

        # context and first input
        assert len(agent.prompt_stack(task1)) == 2

        agent.run()

        agent.add_task(task2)

        # context, memory, and second input
        assert len(agent.prompt_stack(task2)) == 3

    def test_to_prompt_string(self):
        agent = Agent(
            prompt_driver=MockPromptDriver(),
        )

        task = PromptTask("test")

        agent.add_task(task)

        agent.run()

        assert "mock output" in agent.to_prompt_string(task)

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
