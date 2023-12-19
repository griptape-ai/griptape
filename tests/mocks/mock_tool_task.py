import json
from attr import define, field
from griptape.artifacts import BaseArtifact, InfoArtifact
from griptape.tasks import ToolTask
from griptape.tasks import ActionSubtask


@define
class MockToolTask(ToolTask):
    action_name: str = field(default=None)
    action_path: str = field(default=None)
    action_input: dict = field(default=None)

    def run(self) -> BaseArtifact:
        self.active_driver().run(
            prompt_stack=self.prompt_stack
        ).to_text()  # necessary for Completion Chunk Events to publish
        subtask = self.add_subtask(
            ActionSubtask(
                f'Action: {json.dumps({"name": self.action_name, "path": self.action_path, "input": self.action_input})}'
            )
        )
        subtask.execute()

        if subtask.output:
            return subtask.output
        else:
            return InfoArtifact("No tool output")
