from griptape.tasks import PythonTask
from griptape.tasks.python_task import hello_world, deliberate_exception
from tests.mocks.mock_prompt_driver import MockPromptDriver
from griptape.structures import Pipeline


class TestPromptSubtask:
    def test_run(self):
        task = PythonTask("test")
        pipeline = Pipeline(prompt_driver=MockPromptDriver())

        pipeline.add_task(task)

        assert task.run().to_text() == "I'm Done"

    def test_hello_world_fn(self):
        pipeline = Pipeline(prompt_driver=MockPromptDriver(), tasks=[])

        task = PythonTask(
            run_fn= hello_world
        )

        pipeline.add_task(task)


        python_task_var = pipeline.output_task
        assert PythonTask.run(python_task_var).value == "Hello World!"

    def test_error_fn(self):
        pipeline = Pipeline(prompt_driver=MockPromptDriver(), tasks=[])

        task = PythonTask(
            run_fn= deliberate_exception
        )

        pipeline.add_task(task)

        python_task_var = pipeline.output_task
        assert PythonTask.run(python_task_var).value == "error during Python Task execution: ugh blub"
