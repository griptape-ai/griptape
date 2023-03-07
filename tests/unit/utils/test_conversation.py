from warpspeed.steps import PromptStep, ToolStep, ToolkitStep
from warpspeed.artifacts import TextOutput
from warpspeed.structures import Pipeline
from warpspeed.tools import PingPongTool
from warpspeed.utils import Conversation


class TestConversation:
    def test_lines(self):
        pipeline = Pipeline()

        pipeline.add_steps(
            PromptStep("question 1"),
            ToolStep("question 2", tool=PingPongTool())
        )

        pipeline.steps[0].output = TextOutput("answer 1")
        pipeline.steps[1].output = TextOutput("answer 2")

        lines = Conversation(pipeline).lines()

        assert lines[0] == "Q: question 1"
        assert lines[1] == "A: answer 1"
        assert lines[2] == "Q: question 2"
        assert lines[3] == "A: answer 2"

    def test_to_string(self):
        pipeline = Pipeline()

        pipeline.add_steps(
            PromptStep("question 1"),
            ToolStep("question 2", tool=PingPongTool())
        )

        pipeline.steps[0].output = TextOutput("answer 1")
        pipeline.steps[1].output = TextOutput("answer 2")

        string = Conversation(pipeline).to_string()

        assert string == "Q: question 1\nA: answer 1\nQ: question 2\nA: answer 2"
