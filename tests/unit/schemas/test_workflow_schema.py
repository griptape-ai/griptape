from galaxybrain.drivers import OpenAiPromptDriver
from galaxybrain.utils import TiktokenTokenizer
from galaxybrain.workflows import Workflow, PromptStep, ToolStep, ToolkitStep
from galaxybrain.schemas import WorkflowSchema
from galaxybrain.tools import PingPongTool, CalculatorTool, DataScientistTool, EmailTool, WikiTool


class TestWorkflowSchema:
    def test_serialization(self):
        workflow = Workflow(
            prompt_driver=OpenAiPromptDriver(
                tokenizer=TiktokenTokenizer(stop_token="<test>"),
                temperature=0.12345
            )
        )

        tools = [
            PingPongTool(),
            CalculatorTool(),
            DataScientistTool(),
            EmailTool(host="localhost", port=1025, from_email="test@galaxybraintest.com", use_ssl=False),
            WikiTool()
        ]

        workflow.add_steps(
            PromptStep("test prompt"),
            ToolStep("test tool prompt", tool=PingPongTool()),
            ToolkitStep("test router step", tools=tools)
        )

        workflow_dict = WorkflowSchema().dump(workflow)

        assert len(workflow_dict["steps"]) == 3
        assert workflow_dict["steps"][0]["child_id"] == workflow.steps[1].id
        assert workflow_dict["steps"][1]["parent_id"] == workflow.steps[0].id
        assert len(workflow_dict["steps"][-1]["tools"]) == 5
        assert workflow_dict["prompt_driver"]["temperature"] == 0.12345
        assert workflow_dict["prompt_driver"]["tokenizer"]["stop_token"] == "<test>"

    def test_deserialization(self):
        workflow = Workflow(
            prompt_driver=OpenAiPromptDriver(
                tokenizer=TiktokenTokenizer(stop_token="<test>"),
                temperature=0.12345
            )
        )

        tools = [
            PingPongTool(),
            CalculatorTool(),
            DataScientistTool(),
            EmailTool(host="localhost", port=1025, from_email="test@galaxybraintest.com", use_ssl=False),
            WikiTool()
        ]

        workflow.add_steps(
            PromptStep("test prompt"),
            ToolStep("test tool prompt", tool=PingPongTool()),
            ToolkitStep("test router step", tools=tools)
        )

        workflow_dict = WorkflowSchema().dump(workflow)
        deserialized_workflow = WorkflowSchema().load(workflow_dict)

        assert len(deserialized_workflow.steps) == 3
        assert deserialized_workflow.steps[0].child_id == workflow.steps[1].id
        assert deserialized_workflow.steps[1].parent_id == workflow.steps[0].id
        assert len(deserialized_workflow.last_step().tools) == 5
        assert deserialized_workflow.prompt_driver.temperature == 0.12345
        assert deserialized_workflow.prompt_driver.tokenizer.stop_token == "<test>"
