from griptape.drivers import OpenAiAudioTranscriptionDriver
from griptape.loaders import AudioLoader
from griptape.structures import Pipeline
from griptape.tasks import AudioTranscriptionTask

driver = OpenAiAudioTranscriptionDriver(model="whisper-1")

task = AudioTranscriptionTask(
    input=lambda _: AudioLoader().load("tests/resources/sentences2.wav"),
    audio_transcription_driver=driver,
)

Pipeline(tasks=[task]).run()
