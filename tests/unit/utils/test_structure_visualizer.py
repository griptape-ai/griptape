from griptape.drivers import LocalStructureRunDriver
from griptape.structures import Agent, Pipeline, Workflow
from griptape.tasks import PromptTask, StructureRunTask
from griptape.utils import StructureVisualizer


class TestStructureVisualizer:
    def test_agent(self):
        agent = Agent(tasks=[PromptTask("test1", id="task1")])

        visualizer = StructureVisualizer(agent)
        result = visualizer.to_url()

        assert result == "https://mermaid.ink/svg/Z3JhcGggVEQ7CglUYXNrMTs="

    def test_pipeline(self):
        pipeline = Pipeline(
            tasks=[
                PromptTask("test1", id="task1"),
                PromptTask("test2", id="task2"),
                PromptTask("test3", id="task3"),
                PromptTask("test4", id="task4"),
            ],
        )

        visualizer = StructureVisualizer(pipeline)
        result = visualizer.to_url()

        assert (
            result
            == "https://mermaid.ink/svg/Z3JhcGggVEQ7CglUYXNrMS0tPiBUYXNrMjsKCVRhc2syLS0+IFRhc2szOwoJVGFzazMtLT4gVGFzazQ7CglUYXNrNDs="
        )

    def test_workflow(self):
        workflow = Workflow(
            tasks=[
                PromptTask("test1", id="task1"),
                PromptTask("test2", id="task2", parent_ids=["task1"]),
                PromptTask("test3", id="task3", parent_ids=["task1"]),
                PromptTask("test4", id="task4", parent_ids=["task2", "task3"]),
            ],
        )

        visualizer = StructureVisualizer(workflow)
        result = visualizer.to_url()

        assert (
            result
            == "https://mermaid.ink/svg/Z3JhcGggVEQ7CglUYXNrMS0tPiBUYXNrMiAmIFRhc2szOwoJVGFzazItLT4gVGFzazQ7CglUYXNrMy0tPiBUYXNrNDsKCVRhc2s0Ow=="
        )

    def test_structure_run_task(self):
        pipeline = Pipeline(
            tasks=[
                PromptTask("test1", id="task1"),
                StructureRunTask(
                    "test2",
                    structure_run_driver=LocalStructureRunDriver(
                        create_structure=lambda: Pipeline(
                            tasks=[
                                PromptTask("test2a", id="task2a"),
                                PromptTask("test2b", id="task2b"),
                            ],
                        )
                    ),
                    id="task2",
                ),
                PromptTask("test3", id="task3"),
            ],
        )

        visualizer = StructureVisualizer(pipeline)
        result = visualizer.to_url()

        assert (
            result
            == "https://mermaid.ink/svg/Z3JhcGggVEQ7CglUYXNrMS0tPiBUYXNrMjsKCVRhc2syLS0+IFRhc2szOwoJc3ViZ3JhcGggVGFzazIKCVRhc2syQS0tPiBUYXNrMkI7CglUYXNrMkI7CgllbmQKCVRhc2szOw=="
        )

    def test_build_node_id(self):
        assert StructureVisualizer(Pipeline()).build_node_id(PromptTask("test1", id="test1")) == "Test1"
