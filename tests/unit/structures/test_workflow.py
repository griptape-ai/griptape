import pytest
from griptape import tasks

from griptape.memory import ToolMemory
from griptape.memory.tool.storage import TextArtifactStorage
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
        assert workflow.rulesets[0].name == "TestRuleset"
        assert workflow.rulesets[0].rules[0].value == "test"

    def test_rulesets(self):
        workflow = Workflow(rulesets=[Ruleset("Foo", [Rule("foo test")])])

        workflow.add_tasks(
            PromptTask(rulesets=[Ruleset("Bar", [Rule("bar test")])]),
            PromptTask(rulesets=[Ruleset("Baz", [Rule("baz test")])]),
        )

        assert isinstance(workflow.tasks[0], PromptTask)
        assert len(workflow.tasks[0].all_rulesets) == 2
        assert workflow.tasks[0].all_rulesets[0].name == "Foo"
        assert workflow.tasks[0].all_rulesets[1].name == "Bar"

        assert isinstance(workflow.tasks[1], PromptTask)
        assert len(workflow.tasks[1].all_rulesets) == 2
        assert workflow.tasks[1].all_rulesets[0].name == "Foo"
        assert workflow.tasks[1].all_rulesets[1].name == "Baz"

    def test_rules(self):
        workflow = Workflow(rules=[Rule("foo test")])

        workflow.add_tasks(
            PromptTask(rules=[Rule("bar test")]),
            PromptTask(rules=[Rule("baz test")]),
        )

        assert isinstance(workflow.tasks[0], PromptTask)
        assert len(workflow.tasks[0].all_rulesets) == 2
        assert workflow.tasks[0].all_rulesets[0].name == "Default Ruleset"
        assert workflow.tasks[0].all_rulesets[1].name == "Additional Ruleset"

        assert isinstance(workflow.tasks[1], PromptTask)
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

        assert isinstance(workflow.tasks[0], ToolkitTask)
        assert workflow.tasks[0].tools[0].input_memory is not None
        assert (
            workflow.tasks[0].tools[0].input_memory[0] == workflow.tool_memory
        )
        assert workflow.tasks[0].tools[0].output_memory is not None
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

        storage = list(workflow.tool_memory.artifact_storages.values())[0]
        assert isinstance(storage, TextArtifactStorage)
        memory_embedding_driver = (
            storage.query_engine.vector_store_driver.embedding_driver
        )

        assert memory_embedding_driver == embedding_driver

    def test_with_default_tool_memory_and_empty_tool_output_memory(self):
        workflow = Workflow()

        workflow.add_task(ToolkitTask(tools=[MockTool(output_memory={})]))

        assert isinstance(workflow.tasks[0], ToolkitTask)
        assert workflow.tasks[0].tools[0].output_memory == {}

    def test_without_default_tool_memory(self):
        workflow = Workflow(tool_memory=None)

        workflow.add_task(ToolkitTask(tools=[MockTool()]))

        assert isinstance(workflow.tasks[0], ToolkitTask)
        assert workflow.tasks[0].tools[0].input_memory is None
        assert workflow.tasks[0].tools[0].output_memory is None

    def test_tasks_initialization(self):
        first_task = PromptTask(id="test1")
        second_task = PromptTask(id="test2")
        third_task = PromptTask(id="test3")
        workflow = Workflow(tasks=[first_task, second_task, third_task])

        assert len(workflow.tasks) == 3
        assert workflow.tasks[0].id == "test1"
        assert workflow.tasks[1].id == "test2"
        assert workflow.tasks[2].id == "test3"
        assert len(first_task.parents) == 0
        assert len(first_task.children) == 1
        assert len(second_task.parents) == 1
        assert len(second_task.children) == 1
        assert len(third_task.parents) == 1
        assert len(third_task.children) == 0

    def test_add_task(self):
        first_task = PromptTask("test1")
        second_task = PromptTask("test2")

        workflow = Workflow(prompt_driver=MockPromptDriver())

        workflow + first_task
        workflow.add_task(second_task)

        assert len(workflow.tasks) == 2
        assert first_task in workflow.tasks
        assert second_task in workflow.tasks
        assert first_task.structure == workflow
        assert second_task.structure == workflow
        assert len(first_task.parents) == 0
        assert len(first_task.children) == 1
        assert len(second_task.parents) == 1
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
        assert len(first_task.children) == 1
        assert len(second_task.parents) == 1
        assert len(second_task.children) == 0

    def test_run(self):
        workflow = Workflow(prompt_driver=MockPromptDriver())
        task1 = PromptTask("test")
        task2 = PromptTask("test")
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
        task1 = PromptTask("test1", id="task1")
        task2 = PromptTask("test2", id="task2")
        task3 = PromptTask("test3", id="task3")
        task4 = PromptTask("test4", id="task4")
        workflow = Workflow(prompt_driver=MockPromptDriver())

        # task1 splits into task2 and task3
        # task2 and task3 converge into task4
        workflow + task1
        workflow + task4
        workflow.insert_task(task1, task4, task2)
        workflow.insert_task(task1, task4, task3)

        workflow.run()

        assert task1.state == BaseTask.State.FINISHED
        assert task1.parent_ids == []
        assert task1.child_ids == ["task2", "task3"]

        assert task2.state == BaseTask.State.FINISHED
        assert task2.parent_ids == ["task1"]
        assert task2.child_ids == ["task4"]

        assert task3.state == BaseTask.State.FINISHED
        assert task3.parent_ids == ["task1"]
        assert task3.child_ids == ["task4"]

        assert task4.state == BaseTask.State.FINISHED
        assert task4.parent_ids == ["task2", "task3"]
        assert task4.child_ids == []

    def test_run_topology_2(self):
        """Adapted from https://en.wikipedia.org/wiki/Directed_acyclic_graph#/media/File:Tred-G.svg"""
        taska = PromptTask("testa", id="taska")
        taskb = PromptTask("testb", id="taskb")
        taskc = PromptTask("testc", id="taskc")
        taskd = PromptTask("testd", id="taskd")
        taske = PromptTask("teste", id="taske")
        workflow = Workflow(prompt_driver=MockPromptDriver())

        workflow.add_task(taska)
        workflow.add_task(taske)
        workflow.insert_task(taska, taske, taskd, sever=False)
        workflow.insert_task(taska, taskd, taskb, sever=False)
        workflow.insert_task(taska, taskd, taskc, sever=False)
        workflow.insert_task(taska, taske, taskc, sever=False)

        workflow.run()

        assert taska.state == BaseTask.State.FINISHED
        assert taska.parent_ids == []
        assert set(taska.child_ids) == {"taskb", "taskd", "taskc", "taske"}

        assert taskb.state == BaseTask.State.FINISHED
        assert taskb.parent_ids == ["taska"]
        assert taskb.child_ids == ["taskd"]

        assert taskc.state == BaseTask.State.FINISHED
        assert taskc.parent_ids == ["taska"]
        assert set(taskc.child_ids) == {"taskd", "taske"}

        assert taskd.state == BaseTask.State.FINISHED
        assert set(taskd.parent_ids) == {"taskb", "taska", "taskc"}
        assert taskd.child_ids == ["taske"]

        assert taske.state == BaseTask.State.FINISHED
        assert set(taske.parent_ids) == {"taskd", "taskc", "taska"}
        assert taske.child_ids == []

    def test_run_topology_3(self):
        task1 = PromptTask("test1", id="task1")
        task2 = PromptTask("test2", id="task2")
        task3 = PromptTask("test3", id="task3")
        task4 = PromptTask("test4", id="task4")
        workflow = Workflow(prompt_driver=MockPromptDriver())

        workflow + task1
        workflow + task2
        workflow + task3
        workflow.insert_task(task1, task2, task4)

        workflow.run()

        assert task1.state == BaseTask.State.FINISHED
        assert task1.parent_ids == []
        assert task1.child_ids == ["task4"]

        assert task2.state == BaseTask.State.FINISHED
        assert task2.parent_ids == ["task4"]
        assert task2.child_ids == ["task3"]

        assert task3.state == BaseTask.State.FINISHED
        assert task3.parent_ids == ["task2"]
        assert task3.child_ids == []

        assert task4.state == BaseTask.State.FINISHED
        assert task4.parent_ids == ["task1"]
        assert task4.child_ids == ["task2"]

    def test_input_task(self):
        task1 = PromptTask("prompt1")
        task2 = PromptTask("prompt2")
        task3 = PromptTask("prompt3")
        task4 = PromptTask("prompt4")
        workflow = Workflow(prompt_driver=MockPromptDriver())

        workflow + task1
        workflow + task4
        workflow.insert_task(task1, task4, task2)
        workflow.insert_task(task1, task4, task3)

        assert task1 == workflow.input_task

    def test_output_task(self):
        task1 = PromptTask("prompt1")
        task2 = PromptTask("prompt2")
        task3 = PromptTask("prompt3")
        task4 = PromptTask("prompt4")
        workflow = Workflow(prompt_driver=MockPromptDriver())

        workflow + task1
        workflow + task4
        workflow.insert_task(task1, task4, task2)
        workflow.insert_task(task1, task4, task3)

        assert task4 == workflow.output_task

    def test_to_graph(self):
        task1 = PromptTask("prompt1", id="task1")
        task2 = PromptTask("prompt2", id="task2")
        task3 = PromptTask("prompt3", id="task3")
        task4 = PromptTask("prompt4", id="task4")
        workflow = Workflow(prompt_driver=MockPromptDriver())

        workflow + task1
        workflow + task4
        workflow.insert_task(task1, task4, task2)
        workflow.insert_task(task1, task4, task3)

        graph = workflow.to_graph()

        assert graph["task2"] == {"task1"}
        assert graph["task3"] == {"task1"}
        assert graph["task4"] == {"task2", "task3"}

    def test_order_tasks(self):
        task1 = PromptTask("prompt1", id="task1")
        task2 = PromptTask("prompt2", id="task2")
        task3 = PromptTask("prompt3", id="task3")
        task4 = PromptTask("prompt4", id="task4")
        workflow = Workflow(prompt_driver=MockPromptDriver())

        workflow + task1
        workflow + task4
        workflow.insert_task(task1, task4, task2)
        workflow.insert_task(task1, task4, task3)

        ordered_tasks = workflow.order_tasks()

        assert ordered_tasks[0] == task1
        assert ordered_tasks[1] == task2 or ordered_tasks[1] == task3
        assert ordered_tasks[2] == task2 or ordered_tasks[2] == task3
        assert ordered_tasks[3] == task4

    def test_context(self):
        parent = PromptTask("parent")
        task = PromptTask("test")
        child = PromptTask("child")
        workflow = Workflow(prompt_driver=MockPromptDriver())

        workflow + parent
        workflow + task
        workflow + child

        context = workflow.context(task)

        assert context["parent_outputs"] == {parent.id: ""}

        workflow.run()

        context = workflow.context(task)

        assert context["parent_outputs"] == {parent.id: parent.output.to_text()}
        assert context["structure"] == workflow
        assert context["parents"] == {parent.id: parent}
        assert context["children"] == {child.id: child}
