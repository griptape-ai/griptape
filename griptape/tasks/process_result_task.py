from griptape.artifacts import BaseArtifact, TextArtifact
from griptape.tasks import BaseTask


class ProcessResultTask(BaseTask):
    @property
    def input(self) -> BaseArtifact:
        """Retrieve the input artifact from the parent task's output."""
        if self.parents and self.parents[0].output:
            return self.parents[0].output
        raise ValueError("No valid parent output found")

    def try_run(self) -> BaseArtifact:
        """Processes the input artifact and returns a transformed result."""
        input_data = self.input.to_text()
        processed_data = input_data.replace("Alice", "Alice (Processed)")
        return TextArtifact(processed_data)
