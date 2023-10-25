import pytest

from griptape.memory import ToolMemory
from tests.mocks.mock_prompt_driver import MockPromptDriver
from griptape.rules import Rule, Ruleset
from griptape.tasks import PromptTask, BaseTask, ToolkitTask
from griptape.structures import Workflow
from griptape.engines import VectorQueryEngine
from tests.mocks.mock_tool.tool import MockTool
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver


class TestWorkflow:
    def test_init(self):
        driver = MockPromptDriver()
        workflow = Workflow(
            prompt_driver=driver,
            rulesets=[Ruleset("TestRuleset", [Rule("test")])],
        )

        assert workflow.prompt_driver is driver
        assert len(workflow.tasks) == 0
        assert workflow.rulesets[0].name is "TestRuleset"
        assert workflow.rulesets[0].rules[0].value is "test"

    def test_rulesets(self):
        workflow = Workflow(rulesets=[Ruleset("Foo", [Rule("foo test")])])

        workflow.add_tasks(
            PromptTask(rulesets=[Ruleset("Bar", [Rule("bar test")])]),
            PromptTask(rulesets=[Ruleset("Baz", [Rule("baz test")])]),
        )

        assert len(workflow.tasks[0].all_rulesets) == 2
        assert workflow.tasks[0].all_rulesets[0].name == "Foo"
        assert workflow.tasks[0].all_rulesets[1].name == "Bar"

        assert len(workflow.tasks[1].all_rulesets) == 2
        assert workflow.tasks[1].all_rulesets[0].name == "Foo"
        assert workflow.tasks[1].all_rulesets[1].name == "Baz"

    def test_rules(self):
        workflow = Workflow(rules=[Rule("foo test")])

        workflow.add_tasks(
            PromptTask(rules=[Rule("bar test")]),
            PromptTask(rules=[Rule("baz test")]),
        )

        assert len(workflow.tasks[0].all_rulesets) == 2
        assert workflow.tasks[0].all_rulesets[0].name == "Default Ruleset"
        assert workflow.tasks[0].all_rulesets[1].name == "Additional Ruleset"

        assert len(workflow.tasks[1].all_rulesets) == 2
        assert workflow.tasks[1].all_rulesets[0].name == "Default Ruleset"
        assert workflow.tasks[1].all_rulesets[1].name == "Additional Ruleset"

    def test_rules_and_rulesets(self):
        with pytest.raises(ValueError):
            Workflow(
                rules=[Rule("foo test")],
                rulesets=[Ruleset("Bar", [Rule("bar test")])],
            )

        with pytest.raises(ValueError):
            workflow = Workflow()
            workflow.add_task(
                PromptTask(
                    rules=[Rule("foo test")],
                    rulesets=[Ruleset("Bar", [Rule("bar test")])],
                )
            )

    def test_with_default_tool_memory(self):
        workflow = Workflow()

        workflow.add_task(ToolkitTask(tools=[MockTool()]))

        assert isinstance(workflow.tool_memory, ToolMemory)
        assert (
            workflow.tasks[0].tools[0].input_memory[0] == workflow.tool_memory
        )
        assert (
            workflow.tasks[0].tools[0].output_memory["test"][0]
            == workflow.tool_memory
        )
        assert (
            workflow.tasks[0]
            .tools[0]
            .output_memory.get("test_without_default_memory")
            is None
        )

    def test_embedding_driver(self):
        embedding_driver = MockEmbeddingDriver()
        workflow = Workflow(embedding_driver=embedding_driver)

        workflow.add_task(ToolkitTask(tools=[MockTool()]))

        memory_embedding_driver = list(
            workflow.tool_memory.artifact_storages.values()
        )[0].query_engine.vector_store_driver.embedding_driver

        assert memory_embedding_driver == embedding_driver

    def test_with_default_tool_memory_and_empty_tool_output_memory(self):
        workflow = Workflow()

        workflow.add_task(ToolkitTask(tools=[MockTool(output_memory={})]))

        assert workflow.tasks[0].tools[0].output_memory == {}

    def test_without_default_tool_memory(self):
        workflow = Workflow(tool_memory=None)

        workflow.add_task(ToolkitTask(tools=[MockTool()]))

        assert workflow.tasks[0].tools[0].input_memory is None
        assert workflow.tasks[0].tools[0].output_memory is None

    def test_tasks_validation(self):
        with pytest.raises(ValueError):
            Workflow(tasks=[PromptTask()])

    def test_add_task(self):
        first_task = PromptTask("test1")
        second_task = PromptTask("test2")

        workflow = Workflow(prompt_driver=MockPromptDriver())

        workflow + first_task
        workflow + second_task

        assert len(workflow.tasks) == 2
        assert first_task in workflow.tasks
        assert second_task in workflow.tasks
        assert first_task.structure == workflow
        assert second_task.structure == workflow
        assert len(first_task.parents) == 0
        assert len(first_task.children) == 0
        assert len(second_task.parents) == 0
        assert len(second_task.children) == 0

    def test_add_tasks(self):
        first_task = PromptTask("test1")
        second_task = PromptTask("test2")

        workflow = Workflow(prompt_driver=MockPromptDriver())

        workflow + [first_task, second_task]

        assert len(workflow.tasks) == 2
        assert first_task in workflow.tasks
        assert second_task in workflow.tasks
        assert first_task.structure == workflow
        assert second_task.structure == workflow
        assert len(first_task.parents) == 0
        assert len(first_task.children) == 0
        assert len(second_task.parents) == 0
        assert len(second_task.children) == 0

    def test_run(self):
        task1 = PromptTask("test")
        task2 = PromptTask("test")
        workflow = Workflow(prompt_driver=MockPromptDriver())
        workflow + [task1, task2]

        assert task1.state == BaseTask.State.PENDING
        assert task2.state == BaseTask.State.PENDING

        workflow.run()

        assert task1.state == BaseTask.State.FINISHED
        assert task2.state == BaseTask.State.FINISHED

    def test_run_with_args(self):
        task = PromptTask("{{ args[0] }}-{{ args[1] }}")
        workflow = Workflow(prompt_driver=MockPromptDriver())
        workflow + task

        workflow._execution_args = ("test1", "test2")

        assert task.input.to_text() == "test1-test2"

        workflow.run()

        assert task.input.to_text() == "-"

    def test_run_topology_1(self):
        task1 = PromptTask("prompt1")
        task2 = PromptTask("prompt2")
        task3 = PromptTask("prompt3")
        workflow = Workflow(prompt_driver=MockPromptDriver())

        # task1 splits into task2 and task3
        workflow + task1
        task1 >> task2
        task3 << task1

        workflow.run()

        assert task1.state == BaseTask.State.FINISHED
        assert task2.state == BaseTask.State.FINISHED
        assert task3.state == BaseTask.State.FINISHED

    def test_run_topology_2(self):
        task1 = PromptTask("test1")
        task2 = PromptTask("test2")
        task3 = PromptTask("test3")
        workflow = Workflow(prompt_driver=MockPromptDriver())

        # task1 and task2 converge into task3
        workflow + [task1, task2]
        task1 >> task3
        task3 << task2

        workflow.run()

        assert task1.state == BaseTask.State.FINISHED
        assert task2.state == BaseTask.State.FINISHED
        assert task3.state == BaseTask.State.FINISHED

    def test_output_tasks(self):
        task1 = PromptTask("prompt1")
        task2 = PromptTask("prompt2")
        task3 = PromptTask("prompt3")
        workflow = Workflow(prompt_driver=MockPromptDriver())

        workflow + task1
        task1 >> task2
        task3 << task1

        assert len(workflow.output_tasks()) == 2
        assert task2 in workflow.output_tasks()
        assert task3 in workflow.output_tasks()

    def test_to_graph(self):
        task1 = PromptTask("prompt1", id="task1")
        task2 = PromptTask("prompt2", id="task2")
        task3 = PromptTask("prompt3", id="task3")
        workflow = Workflow(prompt_driver=MockPromptDriver())

        workflow + task1
        task1 >> task2
        task3 << task1

        graph = workflow.to_graph()

        assert "task1" in graph["task2"]
        assert "task1" in graph["task3"]

    def test_order_tasks(self):
        task1 = PromptTask("prompt1")
        task2 = PromptTask("prompt2")
        task3 = PromptTask("prompt3")
        workflow = Workflow(prompt_driver=MockPromptDriver())

        workflow + task1
        task1 >> task2
        task3 << task1

        ordered_tasks = workflow.order_tasks()

        assert ordered_tasks[0] == task1
        assert ordered_tasks[1] == task2 or ordered_tasks[1] == task3
        assert ordered_tasks[2] == task2 or ordered_tasks[2] == task3

    def test_context(self):
        parent = PromptTask("parent")
        task = PromptTask("test")
        child = PromptTask("child")
        workflow = Workflow(prompt_driver=MockPromptDriver())

        workflow + parent

        parent >> task
        task >> child

        context = workflow.context(task)

        assert context["parent_outputs"] == {parent.id: ""}

        workflow.run()

        context = workflow.context(task)

        assert context["parent_outputs"] == {parent.id: parent.output.to_text()}
        assert context["structure"] == workflow
        assert context["parents"] == {parent.id: parent}
        assert context["children"] == {child.id: child}
