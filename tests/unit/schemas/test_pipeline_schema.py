from griptape.core.drivers import OpenAiPromptDriver
from griptape.tokenizers import TiktokenTokenizer
from griptape.tasks import PromptTask, ToolkitTask, BaseTask
from griptape.structures import Pipeline
from griptape.schemas import PipelineSchema


class TestPipelineSchema:
    def test_serialization(self):
        pipeline = Pipeline(
            autoprune_memory=False,
            prompt_driver=OpenAiPromptDriver(
                tokenizer=TiktokenTokenizer(stop_sequence="<test>"),
                temperature=0.12345
            )
        )

        tools = [
            "calculator",
            "google_search"
        ]

        task = ToolkitTask("test tool prompt", tool_names=["calculator"])

        pipeline.add_tasks(
            PromptTask("test prompt"),
            task,
            ToolkitTask("test router task", tool_names=tools)
        )

        pipeline_dict = PipelineSchema().dump(pipeline)

        assert pipeline_dict["autoprune_memory"] is False
        assert len(pipeline_dict["tasks"]) == 3
        assert pipeline_dict["tasks"][0]["state"] == "PENDING"
        assert pipeline_dict["tasks"][0]["child_ids"][0] == pipeline.tasks[1].id
        assert pipeline_dict["tasks"][1]["parent_ids"][0] == pipeline.tasks[0].id
        assert len(pipeline_dict["tasks"][-1]["tool_names"]) == 2
        assert pipeline_dict["prompt_driver"]["temperature"] == 0.12345
        assert pipeline_dict["prompt_driver"]["tokenizer"]["stop_sequence"] == "<test>"

    def test_deserialization(self):
        pipeline = Pipeline(
            autoprune_memory=False,
            prompt_driver=OpenAiPromptDriver(
                tokenizer=TiktokenTokenizer(stop_sequence="<test>"),
                temperature=0.12345
            )
        )

        tools = [
            "calculator",
            "google_search"
        ]

        task = ToolkitTask("test tool prompt", tool_names=["calculator"])

        pipeline.add_tasks(
            PromptTask("test prompt"),
            task,
            ToolkitTask("test router task", tool_names=tools)
        )

        workflow_dict = PipelineSchema().dump(pipeline)
        deserialized_pipeline = PipelineSchema().load(workflow_dict)

        assert deserialized_pipeline.autoprune_memory is False
        assert len(deserialized_pipeline.tasks) == 3
        assert deserialized_pipeline.tasks[0].child_ids[0] == pipeline.tasks[1].id
        assert deserialized_pipeline.tasks[0].state == BaseTask.State.PENDING
        assert deserialized_pipeline.tasks[1].parent_ids[0] == pipeline.tasks[0].id
        assert len(deserialized_pipeline.last_task().tool_names) == 2
        assert deserialized_pipeline.prompt_driver.temperature == 0.12345
        assert deserialized_pipeline.prompt_driver.tokenizer.stop_sequence == "<test>"
