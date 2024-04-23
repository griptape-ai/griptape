import elevenlabs

from griptape.artifacts import AudioArtifact


def play_audio(artifact: AudioArtifact) -> AudioArtifact:
    elevenlabs.play(artifact.value)

    return artifact
