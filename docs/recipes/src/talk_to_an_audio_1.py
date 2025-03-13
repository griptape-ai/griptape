from typing import cast

from griptape.artifacts.audio_artifact import AudioArtifact
from griptape.drivers.prompt.openai import OpenAiChatPromptDriver
from griptape.loaders import AudioLoader
from griptape.tasks import PromptTask

prompt_driver = OpenAiChatPromptDriver(
    model="gpt-4o-audio-preview",
    modalities=["audio", "text"],
    audio={"voice": "sage", "format": "mp3"},
)
audio_loader = AudioLoader()
task = PromptTask(prompt_driver=prompt_driver)

audio_file = audio_loader.load("tests/resources/audio.mp3")
result = cast(AudioArtifact, task.run(["Transcribe this audio but like a pirate", audio_file]))
audio_loader.save("pirate_audio.mp3", result)
print(result.meta["transcript"])

result = cast(AudioArtifact, task.run(["What is the tone of the person speaking?", audio_file]))
print(result.meta["transcript"])
