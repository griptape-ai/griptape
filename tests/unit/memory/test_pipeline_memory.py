from skatepark.memory import PipelineMemory, PipelineRun


class TestMemory:
    def test_is_empty(self):
        memory = PipelineMemory()

        assert memory.is_empty()

        memory.add_run(PipelineRun(input="test", output="test"))

        assert not memory.is_empty()

    def test_add_run(self):
        memory = PipelineMemory()
        run = PipelineRun(input="test", output="test")

        memory.add_run(run)

        assert memory.runs[0] == run

    def test_to_string(self):
        memory = PipelineMemory()
        run = PipelineRun(input="test", output="test")

        memory.add_run(run)

        assert "Input: test\nOutput: test" in memory.to_prompt_string()