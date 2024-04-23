import elevenlabs

from griptape.artifacts import AudioArtifact


def play_audio(artifact: AudioArtifact):
    elevenlabs.play(artifact.value)
