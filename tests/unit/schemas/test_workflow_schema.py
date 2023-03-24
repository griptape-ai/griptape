from warpspeed.drivers import OpenAiPromptDriver
from warpspeed.rules import Rule
from warpspeed.utils import TiktokenTokenizer
from warpspeed.steps import PromptStep, ToolStep, ToolkitStep, Step
from warpspeed.structures import Workflow
from warpspeed.schemas import WorkflowSchema
from warpspeed.tools import PingPongTool, CalculatorTool, DataScientistTool, EmailSenderTool, WikiTool


class TestWorkflowSchema:
    def test_serialization(self):
        workflow = Workflow(
            prompt_driver=OpenAiPromptDriver(
                tokenizer=TiktokenTokenizer(stop_sequence="<test>"),
                temperature=0.12345
            ),
            rules=[
                Rule("test rule 1"),
                Rule("test rule 2"),
            ]
        )

        tools = [
            PingPongTool(),
            CalculatorTool(),
            DataScientistTool(),
            EmailSenderTool(host="localhost", port=1025, from_email="test@warpspeedtest.com", use_ssl=False),
            WikiTool()
        ]

        workflow.add_steps(
            PromptStep("test prompt"),
            ToolStep("test tool prompt", tool=PingPongTool())
        )

        step = ToolkitStep("test router step", tools=tools)

        workflow.steps[0].add_child(step)
        workflow.steps[1].add_child(step)

        workflow_dict = WorkflowSchema().dump(workflow)

        assert len(workflow_dict["steps"]) == 3
        assert len(workflow_dict["rules"]) == 2
        assert workflow_dict["steps"][0]["state"] == "PENDING"
        assert workflow_dict["steps"][0]["child_ids"][0] == step.id
        assert workflow.steps[0].id in step.parent_ids
        assert workflow.steps[1].id in step.parent_ids
        assert len(workflow_dict["steps"][-1]["tools"]) == 5
        assert workflow_dict["prompt_driver"]["temperature"] == 0.12345
        assert workflow_dict["prompt_driver"]["tokenizer"]["stop_sequence"] == "<test>"
        assert workflow_dict["rules"][0]["value"] == "test rule 1"

    def test_deserialization(self):
        workflow = Workflow(
            prompt_driver=OpenAiPromptDriver(
                tokenizer=TiktokenTokenizer(stop_sequence="<test>"),
                temperature=0.12345
            ),
            rules=[
                Rule("test rule 1"),
                Rule("test rule 2"),
            ]
        )

        tools = [
            PingPongTool(),
            CalculatorTool(),
            DataScientistTool(),
            EmailSenderTool(host="localhost", port=1025, from_email="test@warpspeedtest.com", use_ssl=False),
            WikiTool()
        ]

        workflow.add_steps(
            PromptStep("test prompt"),
            ToolStep("test tool prompt", tool=PingPongTool())
        )

        step = ToolkitStep("test router step", tools=tools)

        workflow.steps[0].add_child(step)
        workflow.steps[1].add_child(step)

        workflow_dict = WorkflowSchema().dump(workflow)
        deserialized_workflow = WorkflowSchema().load(workflow_dict)

        assert len(deserialized_workflow.steps) == 3
        assert len(deserialized_workflow.rules) == 2
        assert deserialized_workflow.steps[0].child_ids[0] == step.id
        assert deserialized_workflow.steps[0].id in step.parent_ids
        assert deserialized_workflow.steps[1].id in step.parent_ids
        assert len(deserialized_workflow.steps[-1].tools) == 5
        assert deserialized_workflow.prompt_driver.temperature == 0.12345
        assert deserialized_workflow.prompt_driver.tokenizer.stop_sequence == "<test>"
        assert deserialized_workflow.rules[0].value == "test rule 1"
