from tests.mocks.mock_prompt_driver import MockPromptDriver
from tests.mocks.mock_failing_prompt_driver import MockFailingPromptDriver
from griptape.artifacts import ErrorArtifact, TextArtifact
from griptape.tasks import PromptTask
from griptape.structures import Pipeline


class TestPromptDriver:
    def test_run_retries_success(self):
        driver = MockPromptDriver(max_retries=1, retry_delay=0.01)
        pipeline = Pipeline(prompt_driver=driver)

        pipeline.add_task(
            PromptTask("test")
        )

        assert isinstance(pipeline.run().output, TextArtifact)

    def test_run_retries_failure(self):
        driver = MockFailingPromptDriver(max_failures=2, max_retries=1, retry_delay=0.01)
        pipeline = Pipeline(prompt_driver=driver)

        pipeline.add_task(
            PromptTask("test")
        )

        assert isinstance(pipeline.run().output, ErrorArtifact)
