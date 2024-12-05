from griptape.artifacts import InfoArtifact, ListArtifact
from griptape.artifacts.error_artifact import ErrorArtifact
from griptape.structures import Workflow
from griptape.tasks import BaseTask, PromptTask
from griptape.tasks.branch_task import BranchTask


class TestBranchTask:
    def test_one_branch(self):
        def on_run(_: BranchTask) -> InfoArtifact:
            return InfoArtifact("2")

        workflow = Workflow(
            tasks=[
                PromptTask(id="1", child_ids=["branch"]),
                BranchTask(id="branch", on_run=on_run, child_ids=["2", "3"]),
                PromptTask(id="2", child_ids=["4"]),
                PromptTask(id="3", child_ids=["4"]),
                PromptTask(id="4"),
            ]
        )
        workflow.run()

        assert workflow.find_task("1").state == BaseTask.State.FINISHED
        assert workflow.find_task("branch").state == BaseTask.State.FINISHED
        assert workflow.find_task("2").state == BaseTask.State.FINISHED
        assert workflow.find_task("3").state == BaseTask.State.SKIPPED
        assert workflow.find_task("4").state == BaseTask.State.FINISHED
        assert workflow.is_finished()

    def test_multi_branch(self):
        def on_run(_: BranchTask) -> ListArtifact[InfoArtifact]:
            return ListArtifact([InfoArtifact("2"), InfoArtifact("3")])

        workflow = Workflow(
            tasks=[
                PromptTask(id="1", child_ids=["branch"]),
                BranchTask(id="branch", on_run=on_run, child_ids=["2", "3"]),
                PromptTask(id="2", child_ids=["4"]),
                PromptTask(id="3", child_ids=["4"]),
                PromptTask(id="4"),
            ]
        )
        workflow.run()

        assert workflow.find_task("1").state == BaseTask.State.FINISHED
        assert workflow.find_task("branch").state == BaseTask.State.FINISHED
        assert workflow.find_task("2").state == BaseTask.State.FINISHED
        assert workflow.find_task("3").state == BaseTask.State.FINISHED
        assert workflow.find_task("4").state == BaseTask.State.FINISHED
        assert workflow.is_finished()

    def test_no_branch(self):
        def on_run(_: BranchTask) -> ListArtifact[InfoArtifact]:
            return ListArtifact([])

        workflow = Workflow(
            tasks=[
                PromptTask(id="1", child_ids=["branch"]),
                BranchTask(id="branch", on_run=on_run, child_ids=["2", "3"]),
                PromptTask(id="2", child_ids=["4"]),
                PromptTask(id="3", child_ids=["4"]),
                PromptTask(id="4"),
            ]
        )
        workflow.run()

        assert workflow.find_task("1").state == BaseTask.State.FINISHED
        assert workflow.find_task("branch").state == BaseTask.State.FINISHED
        assert workflow.find_task("2").state == BaseTask.State.SKIPPED
        assert workflow.find_task("3").state == BaseTask.State.SKIPPED
        assert workflow.find_task("4").state == BaseTask.State.SKIPPED
        assert workflow.is_finished()

    def test_no_structure(self):
        def on_run(_: BranchTask) -> InfoArtifact:
            return InfoArtifact("2")

        task = BranchTask(input="foo", id="branch", on_run=on_run, child_ids=["2", "3"])
        result = task.run()

        assert result.value == "2"

    def test_bad_branch(self):
        def on_run(_: BranchTask) -> InfoArtifact:
            return InfoArtifact("42")

        workflow = Workflow(
            tasks=[
                PromptTask(id="1", child_ids=["branch"]),
                BranchTask(id="branch", on_run=on_run, child_ids=["2", "3"]),
                PromptTask(id="2", child_ids=["4"]),
                PromptTask(id="3", child_ids=["4"]),
                PromptTask(id="4"),
            ]
        )
        workflow.run()

        assert isinstance(workflow.tasks[1].output, ErrorArtifact)
        assert workflow.tasks[1].output.value == "Branch task returned invalid child task id {'42'}"

        assert workflow.find_task("1").state == BaseTask.State.FINISHED
        assert workflow.find_task("branch").state == BaseTask.State.FINISHED
        assert workflow.find_task("2").state == BaseTask.State.PENDING
        assert workflow.find_task("3").state == BaseTask.State.PENDING
        assert workflow.find_task("4").state == BaseTask.State.PENDING
        assert not workflow.is_finished()
