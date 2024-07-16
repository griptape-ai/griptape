from attrs import define

from griptape.artifacts import TextArtifact
from griptape.tasks.base_audio_input_task import BaseAudioInputTask


@define
class MockAudioInputTask(BaseAudioInputTask):
    def run(self) -> TextArtifact:
        return TextArtifact(self.input.to_text())
