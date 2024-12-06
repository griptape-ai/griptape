import pytest

from griptape.structures import Agent, Pipeline


class TestStructure:
    def test_output(self):
        pipeline = Pipeline()
        with pytest.raises(
            ValueError, match="Structure has no output Task. Add a Task to the Structure to generate output."
        ):
            assert pipeline.output

        agent = Agent()
        with pytest.raises(
            ValueError, match="Structure's output Task has no output. Run the Structure to generate output."
        ):
            assert agent.output
