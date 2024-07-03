import time

import pytest

from pytest import fixture
from griptape.memory.task.storage import TextArtifactStorage
from tests.mocks.mock_prompt_driver import MockPromptDriver
from griptape.rules import Rule, Ruleset
from griptape.tasks import PromptTask, BaseTask, ToolkitTask, CodeExecutionTask, ChoiceControlFlowTask
from griptape.structures import Workflow
from griptape.artifacts import ErrorArtifact, TextArtifact
from griptape.memory.structure import ConversationMemory
from griptape.memory.task.storage import TextArtifactStorage
from griptape.rules import Rule, Ruleset
from griptape.structures import Workflow
from griptape.tasks import BaseTask, CodeExecutionTask, PromptTask, ToolkitTask
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
from tests.mocks.mock_prompt_driver import MockPromptDriver
from tests.mocks.mock_tool.tool import MockTool


class TestWorkflow:
    @pytest.fixture()
    def waiting_task(self):
        def fn(task):
            time.sleep(2)
            return TextArtifact("done")

        return CodeExecutionTask(run_fn=fn)

    @pytest.fixture()
    def error_artifact_task(self):
        def fn(task):
            return ErrorArtifact("error")

        return CodeExecutionTask(run_fn=fn)

    def test_workflow_with_control_flow_task(self):
        task1 = PromptTask("prompt1", id="task1")
        task1.output = TextArtifact("task1 output")
        task2 = PromptTask("prompt2", id="task2")
        task3 = PromptTask("prompt3", id="task3")
        task4 = PromptTask("prompt4", id="end")
        control_flow_task = ChoiceControlFlowTask(id="control_flow_task", control_flow_fn=lambda x: task2)
        control_flow_task.add_parent(task1)
        control_flow_task.add_children([task2, task3])
        task4.add_parents([task2, task3])
        workflow = Workflow(prompt_driver=MockPromptDriver(), tasks=[task1, task2, task3, task4, control_flow_task])
        workflow.resolve_relationships()
        workflow.run()
        from griptape.utils import StructureVisualizer

        print(StructureVisualizer(workflow).to_url())

        assert task1.state == BaseTask.State.FINISHED
        assert task2.state == BaseTask.State.FINISHED
        assert task3.state == BaseTask.State.CANCELLED
        assert task4.state == BaseTask.State.FINISHED
        assert control_flow_task.state == BaseTask.State.FINISHED

    def test_workflow_with_multiple_control_flow_tasks(self):
        # control_flow_task should branch to task3 but
        # task3 should be executed only once
        # and task4 should be CANCELLED
        task1 = PromptTask("prompt1", id="task1")
        task2 = PromptTask("prompt2", id="task2")
        task3 = PromptTask("prompt3", id="task3")
        task4 = PromptTask("prompt4", id="task4")
        task5 = PromptTask("prompt5", id="task5")
        task6 = PromptTask("prompt6", id="task6")
        control_flow_task1 = ChoiceControlFlowTask(id="control_flow_task1", control_flow_fn=lambda x: task3)
        control_flow_task1.add_parent(task1)
        control_flow_task1.add_children([task2, task3])
        control_flow_task2 = ChoiceControlFlowTask(id="control_flow_task2", control_flow_fn=lambda x: task5)
        control_flow_task2.add_parent(task2)
        control_flow_task2.add_children([task4, task5])
        task6.add_parents([task3, task4, task5])
        workflow = Workflow(
            prompt_driver=MockPromptDriver(),
            tasks=[task1, task2, task3, task4, task5, task6, control_flow_task1, control_flow_task2],
        )
        workflow.resolve_relationships()
        workflow.run()
        from griptape.utils import StructureVisualizer

        print(StructureVisualizer(workflow).to_url())

        assert task1.state == BaseTask.State.FINISHED
        assert task2.state == BaseTask.State.CANCELLED
        assert task3.state == BaseTask.State.FINISHED
        assert task4.state == BaseTask.State.CANCELLED
        assert task5.state == BaseTask.State.CANCELLED
        assert task6.state == BaseTask.State.FINISHED
        assert control_flow_task1.state == BaseTask.State.FINISHED
        assert control_flow_task2.state == BaseTask.State.CANCELLED

    def test_workflow_with_control_flow_task_multiple_input_parents(self):
        # control_flow_task should branch to task3 but
        # task3 should be executed only once
        # and task4 should be CANCELLED
        task1 = PromptTask("prompt1", id="task1", prompt_driver=MockPromptDriver(mock_output="3"))
        task2 = PromptTask("prompt2", id="task2")
        task3 = PromptTask(id="task3")
        task4 = PromptTask("prompt4", id="task4")
        task5 = PromptTask("prompt5", id="task5")

        def test(parents) -> tuple:
            return "task3" if parents[0].output.value == "3" else "task4"

        control_flow_task = ChoiceControlFlowTask(id="control_flow_task", control_flow_fn=test)
        control_flow_task.add_parents([task1, task2])
        control_flow_task.add_children([task3, task4])
        task5.add_parents([task3, task4])
        workflow = Workflow(
            prompt_driver=MockPromptDriver(), tasks=[task1, task2, task3, task4, task5, control_flow_task]
        )
        workflow.resolve_relationships()
        workflow.run()

        assert task1.state == BaseTask.State.FINISHED
        assert task2.state == BaseTask.State.FINISHED
        assert task3.state == BaseTask.State.FINISHED
        assert task4.state == BaseTask.State.CANCELLED
        assert task5.state == BaseTask.State.FINISHED
        assert control_flow_task.state == BaseTask.State.FINISHED

    def test_workflow_with_control_flow_task_multiple_child_parents(self):
        # control_flow_task should branch to task3 but
        # task3 should be executed only once
        # and task4 should be CANCELLED
        task1 = PromptTask("prompt1", id="task1")
        task2 = PromptTask("prompt2", id="task2")
        task3 = PromptTask(id="task3")
        task4 = PromptTask("prompt4", id="task4")
        task5 = PromptTask("prompt5", id="task5")
        control_flow_task = ChoiceControlFlowTask(id="control_flow_task", control_flow_fn=lambda x: task3)
        task2.add_parent(task1)
        task2.add_child(task3)
        control_flow_task.add_parent(task1)
        control_flow_task.add_children([task3, task4])
        task5.add_parents([task3, task4])
        workflow = Workflow(
            prompt_driver=MockPromptDriver(), tasks=[task1, task2, task3, task4, task5, control_flow_task]
        )
        workflow.resolve_relationships()
        workflow.run()

        assert task1.state == BaseTask.State.FINISHED
        assert task2.state == BaseTask.State.FINISHED
        assert task3.state == BaseTask.State.FINISHED
        assert task4.state == BaseTask.State.CANCELLED
        assert task5.state == BaseTask.State.FINISHED
        assert control_flow_task.state == BaseTask.State.FINISHED

        for task in [task1, task2, task3, task4, task5, control_flow_task]:
            task.reset()
            assert task.state == BaseTask.State.PENDING
        assert workflow.output is None

        # this time control_flow_task should branch to task4
        # and task3 should still be executed because it has another parent
        control_flow_task.control_flow_fn = lambda x: task4
        workflow.run()

        assert task1.state == BaseTask.State.FINISHED
        assert task2.state == BaseTask.State.FINISHED
        assert task3.state == BaseTask.State.FINISHED
        assert task4.state == BaseTask.State.FINISHED
        assert task5.state == BaseTask.State.FINISHED
        assert control_flow_task.state == BaseTask.State.FINISHED

    def test_init(self):
        driver = MockPromptDriver()
        workflow = Workflow(prompt_driver=driver, rulesets=[Ruleset("TestRuleset", [Rule("test")])])

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

        workflow.add_tasks(PromptTask(rules=[Rule("bar test")]), PromptTask(rules=[Rule("baz test")]))

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
            Workflow(rules=[Rule("foo test")], rulesets=[Ruleset("Bar", [Rule("bar test")])])

        workflow = Workflow()
        with pytest.raises(ValueError):
            workflow.add_task(PromptTask(rules=[Rule("foo test")], rulesets=[Ruleset("Bar", [Rule("bar test")])]))

    def test_with_no_task_memory(self):
        workflow = Workflow()

        workflow.add_task(ToolkitTask(tools=[MockTool()]))

        assert isinstance(workflow.tasks[0], ToolkitTask)
        assert workflow.tasks[0].tools[0].input_memory is not None
        assert workflow.tasks[0].tools[0].input_memory[0] == workflow.task_memory
        assert workflow.tasks[0].tools[0].output_memory is None

    def test_with_task_memory(self):
        workflow = Workflow()

        workflow.add_task(ToolkitTask(tools=[MockTool(off_prompt=True)]))

        assert isinstance(workflow.tasks[0], ToolkitTask)
        assert workflow.tasks[0].tools[0].input_memory is not None
        assert workflow.tasks[0].tools[0].input_memory[0] == workflow.task_memory
        assert workflow.tasks[0].tools[0].output_memory is not None
        assert workflow.tasks[0].tools[0].output_memory["test"][0] == workflow.task_memory

    def test_embedding_driver(self):
        embedding_driver = MockEmbeddingDriver()
        workflow = Workflow(embedding_driver=embedding_driver)

        workflow.add_task(ToolkitTask(tools=[MockTool()]))

        storage = list(workflow.task_memory.artifact_storages.values())[0]
        assert isinstance(storage, TextArtifactStorage)
        memory_embedding_driver = storage.rag_engine.retrieval_stage.retrieval_modules[
            0
        ].vector_store_driver.embedding_driver

        assert memory_embedding_driver == embedding_driver

    def test_with_task_memory_and_empty_tool_output_memory(self):
        workflow = Workflow()

        workflow.add_task(ToolkitTask(tools=[MockTool(output_memory={}, off_prompt=True)]))

        assert isinstance(workflow.tasks[0], ToolkitTask)
        assert workflow.tasks[0].tools[0].output_memory == {}

    def test_without_task_memory(self):
        workflow = Workflow(task_memory=None)

        workflow.add_task(ToolkitTask(tools=[MockTool()]))

        assert isinstance(workflow.tasks[0], ToolkitTask)
        assert workflow.tasks[0].tools[0].input_memory is None
        assert workflow.tasks[0].tools[0].output_memory is None

    def test_with_memory(self):
        first_task = PromptTask("test1")
        second_task = PromptTask("test2")
        third_task = PromptTask("test3")

        workflow = Workflow(prompt_driver=MockPromptDriver(), conversation_memory=ConversationMemory())

        workflow + [first_task, second_task, third_task]

        assert workflow.conversation_memory is not None
        assert len(workflow.conversation_memory.runs) == 0

        workflow.run()
        workflow.run()
        workflow.run()

        assert len(workflow.conversation_memory.runs) == 3

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
        assert len(first_task.children) == 0
        assert len(second_task.parents) == 0
        assert len(second_task.children) == 0
        assert len(third_task.parents) == 0
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

    @pytest.mark.parametrize(
        "tasks",
        [
            [PromptTask(id="task1", parent_ids=["missing"])],
            [PromptTask(id="task1", child_ids=["missing"])],
            [PromptTask(id="task1"), PromptTask(id="task2", parent_ids=["missing"])],
            [PromptTask(id="task1"), PromptTask(id="task2", parent_ids=["task1", "missing"])],
            [PromptTask(id="task1"), PromptTask(id="task2", parent_ids=["task1"], child_ids=["missing"])],
        ],
    )
    def test_run_raises_on_missing_parent_or_child_id(self, tasks):
        workflow = Workflow(prompt_driver=MockPromptDriver(), tasks=tasks)

        with pytest.raises(ValueError) as e:
            workflow.run()

        assert e.value.args[0] == "Task with id missing doesn't exist."

    def test_run_topology_1_declarative_parents(self):
        workflow = Workflow(
            prompt_driver=MockPromptDriver(),
            tasks=[
                PromptTask("test1", id="task1"),
                PromptTask("test2", id="task2", parent_ids=["task1"]),
                PromptTask("test3", id="task3", parent_ids=["task1"]),
                PromptTask("test4", id="task4", parent_ids=["task2", "task3"]),
            ],
        )

        workflow.run()

        self._validate_topology_1(workflow)

    def test_run_topology_1_declarative_children(self):
        workflow = Workflow(
            prompt_driver=MockPromptDriver(),
            tasks=[
                PromptTask("test1", id="task1", child_ids=["task2", "task3"]),
                PromptTask("test2", id="task2", child_ids=["task4"]),
                PromptTask("test3", id="task3", child_ids=["task4"]),
                PromptTask("test4", id="task4"),
            ],
        )

        workflow.run()

        self._validate_topology_1(workflow)

    def test_run_topology_1_declarative_mixed(self):
        workflow = Workflow(
            prompt_driver=MockPromptDriver(),
            tasks=[
                PromptTask("test1", id="task1", child_ids=["task3"]),
                PromptTask("test2", id="task2", parent_ids=["task1"], child_ids=["task4"]),
                PromptTask("test3", id="task3"),
                PromptTask("test4", id="task4", parent_ids=["task2", "task3"]),
            ],
        )

        workflow.run()

        self._validate_topology_1(workflow)

    def test_run_topology_1_imperative_parents(self):
        task1 = PromptTask("test1", id="task1")
        task2 = PromptTask("test2", id="task2")
        task3 = PromptTask("test3", id="task3")
        task4 = PromptTask("test4", id="task4")
        task2.add_parent(task1)
        task3.add_parent("task1")
        task4.add_parents([task2, "task3"])
        workflow = Workflow(prompt_driver=MockPromptDriver(), tasks=[task1, task2, task3, task4])

        workflow.run()

        self._validate_topology_1(workflow)

    def test_run_topology_1_imperative_children(self):
        task1 = PromptTask("test1", id="task1")
        task2 = PromptTask("test2", id="task2")
        task3 = PromptTask("test3", id="task3")
        task4 = PromptTask("test4", id="task4")
        task1.add_children([task2, task3])
        task2.add_child(task4)
        task3.add_child(task4)
        workflow = Workflow(prompt_driver=MockPromptDriver(), tasks=[task1, task2, task3, task4])

        workflow.run()

        self._validate_topology_1(workflow)

    def test_run_topology_1_imperative_mixed(self):
        task1 = PromptTask("test1", id="task1")
        task2 = PromptTask("test2", id="task2")
        task3 = PromptTask("test3", id="task3")
        task4 = PromptTask("test4", id="task4")
        task1.add_children([task2, task3])
        task4.add_parents([task2, task3])
        workflow = Workflow(prompt_driver=MockPromptDriver(), tasks=[task1, task2, task3, task4])

        workflow.run()

        self._validate_topology_1(workflow)

    def test_run_topology_1_imperative_insert(self):
        task1 = PromptTask("test1", id="task1")
        task2 = PromptTask("test2", id="task2")
        task3 = PromptTask("test3", id="task3")
        task4 = PromptTask("test4", id="task4")
        workflow = Workflow(prompt_driver=MockPromptDriver())

        # task1 splits into task2 and task3
        # task2 and task3 converge into task4
        workflow + task1
        workflow + task4
        workflow.insert_tasks(task1, [task2, task3], task4)

        workflow.run()

        self._validate_topology_1(workflow)

    def test_run_topology_1_missing_parent(self):
        task1 = PromptTask("test1", id="task1")
        task2 = PromptTask("test2", id="task2")
        task3 = PromptTask("test3", id="task3")
        task4 = PromptTask("test4", id="task4")
        workflow = Workflow(prompt_driver=MockPromptDriver())

        # task1 never added to workflow
        workflow + task4
        with pytest.raises(ValueError):
            workflow.insert_tasks(task1, [task2, task3], task4)

    def test_run_topology_1_id_equality(self):
        task1 = PromptTask("test1", id="task1")
        task2 = PromptTask("test2", id="task2")
        task3 = PromptTask("test3", id="task3")
        task4 = PromptTask("test4", id="task4")
        workflow = Workflow(prompt_driver=MockPromptDriver())

        # task4 never added to workflow
        workflow + task1
        workflow.insert_tasks(task1, [task2, task3], task4)

        with pytest.raises(ValueError):
            workflow.run()

    def test_run_topology_1_object_equality(self):
        task1 = PromptTask("test1", id="task1")
        task2 = PromptTask("test2", id="task2")
        task3 = PromptTask("test3", id="task3")
        task4 = PromptTask("test4", id="task4")
        workflow = Workflow(prompt_driver=MockPromptDriver())

        workflow + task1
        workflow + task4
        with pytest.raises(ValueError):
            workflow.insert_tasks(PromptTask("test1", id="task1"), [task2, task3], task4)

    def test_run_topology_2_declarative_parents(self):
        workflow = Workflow(
            prompt_driver=MockPromptDriver(),
            tasks=[
                PromptTask("testa", id="taska"),
                PromptTask("testb", id="taskb", parent_ids=["taska"]),
                PromptTask("testc", id="taskc", parent_ids=["taska"]),
                PromptTask("testd", id="taskd", parent_ids=["taska", "taskb", "taskc"]),
                PromptTask("teste", id="taske", parent_ids=["taska", "taskd", "taskc"]),
            ],
        )

        workflow.run()

        self._validate_topology_2(workflow)

    def test_run_topology_2_declarative_children(self):
        workflow = Workflow(
            prompt_driver=MockPromptDriver(),
            tasks=[
                PromptTask("testa", id="taska", child_ids=["taskb", "taskc", "taskd", "taske"]),
                PromptTask("testb", id="taskb", child_ids=["taskd"]),
                PromptTask("testc", id="taskc", child_ids=["taskd", "taske"]),
                PromptTask("testd", id="taskd", child_ids=["taske"]),
                PromptTask("teste", id="taske", child_ids=[]),
            ],
        )

        workflow.run()

        self._validate_topology_2(workflow)

    def test_run_topology_2_imperative_parents(self):
        taska = PromptTask("testa", id="taska")
        taskb = PromptTask("testb", id="taskb")
        taskc = PromptTask("testc", id="taskc")
        taskd = PromptTask("testd", id="taskd")
        taske = PromptTask("teste", id="taske")
        taskb.add_parent(taska)
        taskc.add_parent("taska")
        taskd.add_parents([taska, taskb, taskc])
        taske.add_parents(["taska", taskd, "taskc"])
        workflow = Workflow(prompt_driver=MockPromptDriver(), tasks=[taska, taskb, taskc, taskd, taske])

        workflow.run()

        self._validate_topology_2(workflow)

    def test_run_topology_2_imperative_children(self):
        taska = PromptTask("testa", id="taska")
        taskb = PromptTask("testb", id="taskb")
        taskc = PromptTask("testc", id="taskc")
        taskd = PromptTask("testd", id="taskd")
        taske = PromptTask("teste", id="taske")
        taska.add_children([taskb, taskc, taskd, taske])
        taskb.add_child(taskd)
        taskc.add_children([taskd, taske])
        taskd.add_child(taske)
        workflow = Workflow(prompt_driver=MockPromptDriver(), tasks=[taska, taskb, taskc, taskd, taske])

        workflow.run()

        self._validate_topology_2(workflow)

    def test_run_topology_2_imperative_mixed(self):
        taska = PromptTask("testa", id="taska")
        taskb = PromptTask("testb", id="taskb")
        taskc = PromptTask("testc", id="taskc")
        taskd = PromptTask("testd", id="taskd")
        taske = PromptTask("teste", id="taske")
        taska.add_children([taskb, taskc, taskd, taske])
        taskb.add_child(taskd)
        taskd.add_parent(taskc)
        taske.add_parents(["taska", taskd, "taskc"])
        workflow = Workflow(prompt_driver=MockPromptDriver(), tasks=[taska, taskb, taskc, taskd, taske])

        workflow.run()

        self._validate_topology_2(workflow)

    def test_run_topology_2_imperative_insert(self):
        taska = PromptTask("testa", id="taska")
        taskb = PromptTask("testb", id="taskb")
        taskc = PromptTask("testc", id="taskc")
        taskd = PromptTask("testd", id="taskd")
        taske = PromptTask("teste", id="taske")
        workflow = Workflow(prompt_driver=MockPromptDriver())
        workflow.add_task(taska)
        workflow.add_task(taske)
        taske.add_parent(taska)
        workflow.insert_tasks(taska, taskd, taske, preserve_relationship=True)
        workflow.insert_tasks(taska, [taskc], [taskd, taske], preserve_relationship=True)
        workflow.insert_tasks(taska, taskb, taskd, preserve_relationship=True)

        workflow.run()

        self._validate_topology_2(workflow)

    def test_run_topology_3_declarative_parents(self):
        workflow = Workflow(
            prompt_driver=MockPromptDriver(),
            tasks=[
                PromptTask("test1", id="task1"),
                PromptTask("test2", id="task2", parent_ids=["task4"]),
                PromptTask("test4", id="task4", parent_ids=["task1"]),
                PromptTask("test3", id="task3", parent_ids=["task2"]),
            ],
        )

        workflow.run()

        self._validate_topology_3(workflow)

    def test_run_topology_3_declarative_children(self):
        workflow = Workflow(
            prompt_driver=MockPromptDriver(),
            tasks=[
                PromptTask("test1", id="task1", child_ids=["task4"]),
                PromptTask("test2", id="task2", child_ids=["task3"]),
                PromptTask("test4", id="task4", child_ids=["task2"]),
                PromptTask("test3", id="task3", child_ids=[]),
            ],
        )

        workflow.run()

        self._validate_topology_3(workflow)

    def test_run_topology_3_declarative_mixed(self):
        workflow = Workflow(
            prompt_driver=MockPromptDriver(),
            tasks=[
                PromptTask("test1", id="task1"),
                PromptTask("test2", id="task2", parent_ids=["task4"], child_ids=["task3"]),
                PromptTask("test4", id="task4", parent_ids=["task1"], child_ids=["task2"]),
                PromptTask("test3", id="task3"),
            ],
        )

        workflow.run()

        self._validate_topology_3(workflow)

    def test_run_topology_3_imperative_insert(self):
        task1 = PromptTask("test1", id="task1")
        task2 = PromptTask("test2", id="task2")
        task3 = PromptTask("test3", id="task3")
        task4 = PromptTask("test4", id="task4")
        workflow = Workflow(prompt_driver=MockPromptDriver())

        workflow + task1
        workflow + task2
        workflow + task3
        task2.add_parent(task1)
        task3.add_parent(task2)
        workflow.insert_tasks(task1, task4, task2)

        workflow.run()

        self._validate_topology_3(workflow)

    def test_run_topology_4_declarative_parents(self):
        workflow = Workflow(
            prompt_driver=MockPromptDriver(),
            tasks=[
                PromptTask(id="collect_movie_info"),
                PromptTask(id="movie_info_1", parent_ids=["collect_movie_info"]),
                PromptTask(id="movie_info_2", parent_ids=["collect_movie_info"]),
                PromptTask(id="movie_info_3", parent_ids=["collect_movie_info"]),
                PromptTask(id="compare_movies", parent_ids=["movie_info_1", "movie_info_2", "movie_info_3"]),
                PromptTask(id="send_email_task", parent_ids=["compare_movies"]),
                PromptTask(id="save_to_disk", parent_ids=["compare_movies"]),
                PromptTask(id="publish_website", parent_ids=["compare_movies"]),
                PromptTask(id="summarize_to_slack", parent_ids=["send_email_task", "save_to_disk", "publish_website"]),
            ],
        )

        workflow.run()

        self._validate_topology_4(workflow)

    def test_run_topology_4_declarative_children(self):
        workflow = Workflow(
            prompt_driver=MockPromptDriver(),
            tasks=[
                PromptTask(id="collect_movie_info", child_ids=["movie_info_1", "movie_info_2", "movie_info_3"]),
                PromptTask(id="movie_info_1", child_ids=["compare_movies"]),
                PromptTask(id="movie_info_2", child_ids=["compare_movies"]),
                PromptTask(id="movie_info_3", child_ids=["compare_movies"]),
                PromptTask(id="compare_movies", child_ids=["send_email_task", "save_to_disk", "publish_website"]),
                PromptTask(id="send_email_task", child_ids=["summarize_to_slack"]),
                PromptTask(id="save_to_disk", child_ids=["summarize_to_slack"]),
                PromptTask(id="publish_website", child_ids=["summarize_to_slack"]),
                PromptTask(id="summarize_to_slack", child_ids=[]),
            ],
        )

        workflow.run()

        self._validate_topology_4(workflow)

    def test_run_topology_4_declarative_mixed(self):
        workflow = Workflow(
            prompt_driver=MockPromptDriver(),
            tasks=[
                PromptTask(id="collect_movie_info"),
                PromptTask(id="movie_info_1", parent_ids=["collect_movie_info"], child_ids=["compare_movies"]),
                PromptTask(id="movie_info_2", parent_ids=["collect_movie_info"], child_ids=["compare_movies"]),
                PromptTask(id="movie_info_3", parent_ids=["collect_movie_info"], child_ids=["compare_movies"]),
                PromptTask(id="compare_movies"),
                PromptTask(id="send_email_task", parent_ids=["compare_movies"], child_ids=["summarize_to_slack"]),
                PromptTask(id="save_to_disk", parent_ids=["compare_movies"], child_ids=["summarize_to_slack"]),
                PromptTask(id="publish_website", parent_ids=["compare_movies"], child_ids=["summarize_to_slack"]),
                PromptTask(id="summarize_to_slack"),
            ],
        )

        workflow.run()

        self._validate_topology_4(workflow)

    def test_run_topology_4_imperative_insert(self):
        collect_movie_info = PromptTask(id="collect_movie_info")
        summarize_to_slack = PromptTask(id="summarize_to_slack")
        movie_info_1 = PromptTask(id="movie_info_1")
        movie_info_2 = PromptTask(id="movie_info_2")
        movie_info_3 = PromptTask(id="movie_info_3")
        compare_movies = PromptTask(id="compare_movies")
        send_email_task = PromptTask(id="send_email_task")
        save_to_disk = PromptTask(id="save_to_disk")
        publish_website = PromptTask(id="publish_website")
        movie_info_3 = PromptTask(id="movie_info_3")

        workflow = Workflow(prompt_driver=MockPromptDriver())
        workflow.add_tasks(collect_movie_info, summarize_to_slack)
        workflow.insert_tasks(collect_movie_info, [movie_info_1, movie_info_2, movie_info_3], summarize_to_slack)
        workflow.insert_tasks([movie_info_1, movie_info_2, movie_info_3], compare_movies, summarize_to_slack)
        workflow.insert_tasks(compare_movies, [send_email_task, save_to_disk, publish_website], summarize_to_slack)

        self._validate_topology_4(workflow)

    @pytest.mark.parametrize(
        "tasks",
        [
            [PromptTask(id="a", parent_ids=["a"])],
            [PromptTask(id="a"), PromptTask(id="b", parent_ids=["a", "b"])],
            [PromptTask(id="a", parent_ids=["b"]), PromptTask(id="b", parent_ids=["a"])],
            [
                PromptTask(id="a", parent_ids=["c"]),
                PromptTask(id="b", parent_ids=["a"]),
                PromptTask(id="c", parent_ids=["b"]),
            ],
        ],
    )
    def test_run_raises_on_cycle(self, tasks):
        workflow = Workflow(prompt_driver=MockPromptDriver(), tasks=tasks)

        with pytest.raises(ValueError) as e:
            workflow.run()

        assert e.value.args[0] == "nodes are in a cycle"

    def test_input_task(self):
        task1 = PromptTask("prompt1")
        task2 = PromptTask("prompt2")
        task3 = PromptTask("prompt3")
        task4 = PromptTask("prompt4")
        workflow = Workflow(prompt_driver=MockPromptDriver())

        workflow + task1
        workflow + task4
        workflow.insert_tasks(task1, [task2, task3], task4)

        assert task1 == workflow.input_task

    def test_output_task(self):
        task1 = PromptTask("prompt1")
        task2 = PromptTask("prompt2")
        task3 = PromptTask("prompt3")
        task4 = PromptTask("prompt4")
        workflow = Workflow(prompt_driver=MockPromptDriver())

        workflow + task1
        workflow + task4
        workflow.insert_tasks(task1, [task2, task3], task4)

        assert task4 == workflow.output_task

        task4.add_parents([task2, task3])
        task1.add_children([task2, task3])

        # task4 is the final task, but its defined at index 0
        workflow = Workflow(prompt_driver=MockPromptDriver(), tasks=[task4, task1, task2, task3])

        # output_task topologically should be task4
        assert task4 == workflow.output_task

    def test_to_graph(self):
        task1 = PromptTask("prompt1", id="task1")
        task2 = PromptTask("prompt2", id="task2")
        task3 = PromptTask("prompt3", id="task3")
        task4 = PromptTask("prompt4", id="task4")
        workflow = Workflow(prompt_driver=MockPromptDriver())

        workflow + task1
        workflow + task4
        workflow.insert_tasks(task1, [task2, task3], task4)

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
        workflow.insert_tasks(task1, [task2, task3], task4)

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

        task.add_parent(parent)
        task.add_child(child)

        context = workflow.context(task)

        assert context["parent_outputs"] == {parent.id: ""}

        workflow.run()

        context = workflow.context(task)

        assert context["parent_outputs"] == {parent.id: parent.output.to_text()}
        assert context["parents_output_text"] == "mock output"
        assert context["structure"] == workflow
        assert context["parents"] == {parent.id: parent}
        assert context["children"] == {child.id: child}

    def test_deprecation(self):
        with pytest.deprecated_call():
            Workflow(prompt_driver=MockPromptDriver())

        with pytest.deprecated_call():
            Workflow(embedding_driver=MockEmbeddingDriver())

        with pytest.deprecated_call():
            Workflow(stream=True)

    def test_run_with_error_artifact(self, error_artifact_task, waiting_task):
        end_task = PromptTask("end")
        end_task.add_parents([error_artifact_task, waiting_task])
        workflow = Workflow(prompt_driver=MockPromptDriver(), tasks=[waiting_task, error_artifact_task, end_task])
        workflow.run()

        assert workflow.output is None

    def test_run_with_error_artifact_no_fail_fast(self, error_artifact_task, waiting_task):
        end_task = PromptTask("end")
        end_task.add_parents([error_artifact_task, waiting_task])
        workflow = Workflow(
            prompt_driver=MockPromptDriver(), tasks=[waiting_task, error_artifact_task, end_task], fail_fast=False
        )
        workflow.run()

        assert workflow.output is not None

    @staticmethod
    def _validate_topology_1(workflow) -> None:
        assert len(workflow.tasks) == 4
        assert workflow.input_task.id == "task1"
        assert workflow.output_task.id == "task4"
        assert workflow.input_task.id == workflow.tasks[0].id
        assert workflow.output_task.id == workflow.tasks[-1].id

        task1 = workflow.find_task("task1")
        assert task1.state == BaseTask.State.FINISHED
        assert task1.parent_ids == []
        assert sorted(task1.child_ids) == ["task2", "task3"]

        task2 = workflow.find_task("task2")
        assert task2.state == BaseTask.State.FINISHED
        assert task2.parent_ids == ["task1"]
        assert task2.child_ids == ["task4"]

        task3 = workflow.find_task("task3")
        assert task3.state == BaseTask.State.FINISHED
        assert task3.parent_ids == ["task1"]
        assert task3.child_ids == ["task4"]

        task4 = workflow.find_task("task4")
        assert task4.state == BaseTask.State.FINISHED
        assert sorted(task4.parent_ids) == ["task2", "task3"]
        assert task4.child_ids == []

    @staticmethod
    def _validate_topology_2(workflow) -> None:
        """Adapted from https://en.wikipedia.org/wiki/Directed_acyclic_graph#/media/File:Tred-G.svg."""
        assert len(workflow.tasks) == 5
        assert workflow.input_task.id == "taska"
        assert workflow.output_task.id == "taske"
        assert workflow.input_task.id == workflow.tasks[0].id
        assert workflow.output_task.id == workflow.tasks[-1].id

        taska = workflow.find_task("taska")
        assert taska.state == BaseTask.State.FINISHED
        assert taska.parent_ids == []
        assert sorted(taska.child_ids) == ["taskb", "taskc", "taskd", "taske"]

        taskb = workflow.find_task("taskb")
        assert taskb.state == BaseTask.State.FINISHED
        assert taskb.parent_ids == ["taska"]
        assert taskb.child_ids == ["taskd"]

        taskc = workflow.find_task("taskc")
        assert taskc.state == BaseTask.State.FINISHED
        assert taskc.parent_ids == ["taska"]
        assert sorted(taskc.child_ids) == ["taskd", "taske"]

        taskd = workflow.find_task("taskd")
        assert taskd.state == BaseTask.State.FINISHED
        assert sorted(taskd.parent_ids) == ["taska", "taskb", "taskc"]
        assert taskd.child_ids == ["taske"]

        taske = workflow.find_task("taske")
        assert taske.state == BaseTask.State.FINISHED
        assert sorted(taske.parent_ids) == ["taska", "taskc", "taskd"]
        assert taske.child_ids == []

    @staticmethod
    def _validate_topology_3(workflow) -> None:
        assert len(workflow.tasks) == 4
        assert workflow.input_task.id == "task1"
        assert workflow.output_task.id == "task3"
        assert workflow.input_task.id == workflow.tasks[0].id
        assert workflow.output_task.id == workflow.tasks[-1].id

        task1 = workflow.find_task("task1")
        assert task1.state == BaseTask.State.FINISHED
        assert task1.parent_ids == []
        assert task1.child_ids == ["task4"]

        task2 = workflow.find_task("task2")
        assert task2.state == BaseTask.State.FINISHED
        assert task2.parent_ids == ["task4"]
        assert task2.child_ids == ["task3"]

        task3 = workflow.find_task("task3")
        assert task3.state == BaseTask.State.FINISHED
        assert task3.parent_ids == ["task2"]
        assert task3.child_ids == []

        task4 = workflow.find_task("task4")
        assert task4.state == BaseTask.State.FINISHED
        assert task4.parent_ids == ["task1"]
        assert task4.child_ids == ["task2"]

    @staticmethod
    def _validate_topology_4(workflow) -> None:
        assert len(workflow.tasks) == 9
        assert workflow.input_task.id == "collect_movie_info"
        assert workflow.output_task.id == "summarize_to_slack"
        assert workflow.input_task.id == workflow.tasks[0].id
        assert workflow.output_task.id == workflow.tasks[-1].id

        collect_movie_info = workflow.find_task("collect_movie_info")
        assert collect_movie_info.parent_ids == []
        assert sorted(collect_movie_info.child_ids) == ["movie_info_1", "movie_info_2", "movie_info_3"]

        movie_info_1 = workflow.find_task("movie_info_1")
        assert movie_info_1.parent_ids == ["collect_movie_info"]
        assert movie_info_1.child_ids == ["compare_movies"]

        movie_info_2 = workflow.find_task("movie_info_2")
        assert movie_info_2.parent_ids == ["collect_movie_info"]
        assert movie_info_2.child_ids == ["compare_movies"]

        movie_info_3 = workflow.find_task("movie_info_3")
        assert movie_info_3.parent_ids == ["collect_movie_info"]
        assert movie_info_3.child_ids == ["compare_movies"]

        compare_movies = workflow.find_task("compare_movies")
        assert sorted(compare_movies.parent_ids) == ["movie_info_1", "movie_info_2", "movie_info_3"]
        assert sorted(compare_movies.child_ids) == ["publish_website", "save_to_disk", "send_email_task"]

        send_email_task = workflow.find_task("send_email_task")
        assert send_email_task.parent_ids == ["compare_movies"]
        assert send_email_task.child_ids == ["summarize_to_slack"]

        save_to_disk = workflow.find_task("save_to_disk")
        assert save_to_disk.parent_ids == ["compare_movies"]
        assert save_to_disk.child_ids == ["summarize_to_slack"]

        publish_website = workflow.find_task("publish_website")
        assert publish_website.parent_ids == ["compare_movies"]
        assert publish_website.child_ids == ["summarize_to_slack"]
