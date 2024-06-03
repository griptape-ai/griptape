import pytest

from griptape.memory.task.storage import TextArtifactStorage
from tests.mocks.mock_prompt_driver import MockPromptDriver
from griptape.rules import Rule, Ruleset
from griptape.tasks import PromptTask, BaseTask, ToolkitTask
from griptape.structures import Workflow
from griptape.memory.structure import ConversationMemory
from tests.mocks.mock_tool.tool import MockTool
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver


class TestWorkflow:
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

        with pytest.raises(ValueError):
            workflow = Workflow()
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
        memory_embedding_driver = storage.query_engine.vector_store_driver.embedding_driver

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
        workflow.insert_tasks(taska, taskd, taske, preserve_relationship=True)
        workflow.insert_tasks(taska, [taskc], [taskd, taske], preserve_relationship=True)
        workflow.insert_tasks(taska, taskb, taskd, preserve_relationship=True)

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
        workflow.insert_tasks(task1, task4, task2)

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

    def test_run_topology_4(self):
        workflow = Workflow(prompt_driver=MockPromptDriver())
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

        workflow.add_tasks(collect_movie_info, summarize_to_slack)
        workflow.insert_tasks(collect_movie_info, [movie_info_1, movie_info_2, movie_info_3], summarize_to_slack)
        workflow.insert_tasks([movie_info_1, movie_info_2, movie_info_3], compare_movies, summarize_to_slack)
        workflow.insert_tasks(compare_movies, [send_email_task, save_to_disk, publish_website], summarize_to_slack)

        assert set(collect_movie_info.child_ids) == {"movie_info_1", "movie_info_2", "movie_info_3"}

        assert set(movie_info_1.parent_ids) == {"collect_movie_info"}
        assert set(movie_info_2.parent_ids) == {"collect_movie_info"}
        assert set(movie_info_3.parent_ids) == {"collect_movie_info"}
        assert set(movie_info_1.child_ids) == {"compare_movies"}
        assert set(movie_info_2.child_ids) == {"compare_movies"}
        assert set(movie_info_3.child_ids) == {"compare_movies"}

        assert set(compare_movies.parent_ids) == {"movie_info_1", "movie_info_2", "movie_info_3"}
        assert set(compare_movies.child_ids) == {"send_email_task", "save_to_disk", "publish_website"}

        assert set(send_email_task.parent_ids) == {"compare_movies"}
        assert set(save_to_disk.parent_ids) == {"compare_movies"}
        assert set(publish_website.parent_ids) == {"compare_movies"}

        assert set(send_email_task.child_ids) == {"summarize_to_slack"}
        assert set(save_to_disk.child_ids) == {"summarize_to_slack"}
        assert set(publish_website.child_ids) == {"summarize_to_slack"}

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

        context = workflow.context(task)

        assert context["parent_outputs"] == {parent.id: ""}

        workflow.run()

        context = workflow.context(task)

        assert context["parent_outputs"] == {parent.id: parent.output.to_text()}
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
