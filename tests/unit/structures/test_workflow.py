import json

from griptape.rules.ruleset import Ruleset
from tests.mocks.mock_driver import MockDriver
from griptape.rules import Rule
from griptape.tasks import PromptTask, BaseTask
from griptape.structures import Workflow


class TestWorkflow:
    def test_constructor(self):
        rule = Rule("test")
        driver = MockDriver()
        workflow = Workflow(prompt_driver=driver, rulesets=[Ruleset("TestRuleset", [Rule("test")])])

        assert workflow.prompt_driver is driver
        assert len(workflow.tasks) == 0
        assert workflow.rulesets[0].name is "TestRuleset"
        assert workflow.rulesets[0].rules[0].value is "test"

    def test_add_task(self):
        first_task = PromptTask("test1")
        second_task = PromptTask("test2")

        workflow = Workflow(
            prompt_driver=MockDriver()
        )

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

        workflow = Workflow(
            prompt_driver=MockDriver()
        )

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
        workflow = Workflow(prompt_driver=MockDriver())
        workflow + [task1, task2]

        assert task1.state == BaseTask.State.PENDING
        assert task2.state == BaseTask.State.PENDING

        workflow.run()

        assert task1.state == BaseTask.State.FINISHED
        assert task2.state == BaseTask.State.FINISHED

    def test_run_with_args(self):
        task = PromptTask("{{ args[0] }}-{{ args[1] }}")
        workflow = Workflow(prompt_driver=MockDriver())
        workflow + task

        workflow._execution_args = ("test1", "test2")

        assert task.input.value == "test1-test2"

        workflow.run()

        assert task.input.value == "-"

    def test_run_topology_1(self):
        task1 = PromptTask("prompt1")
        task2 = PromptTask("prompt2")
        task3 = PromptTask("prompt3")
        workflow = Workflow(prompt_driver=MockDriver())

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
        workflow = Workflow(prompt_driver=MockDriver())

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
        workflow = Workflow(prompt_driver=MockDriver())

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
        workflow = Workflow(prompt_driver=MockDriver())

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
        workflow = Workflow(prompt_driver=MockDriver())

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
        workflow = Workflow(prompt_driver=MockDriver())

        workflow + parent

        parent >> task
        task >> child

        context = workflow.context(task)

        assert context["inputs"] == {parent.id: ""}

        workflow.run()

        context = workflow.context(task)

        assert context["inputs"] == {parent.id: parent.output.value}
        assert context["structure"] == workflow
        assert context["parents"] == {parent.id: parent}
        assert context["children"] == {child.id: child}
