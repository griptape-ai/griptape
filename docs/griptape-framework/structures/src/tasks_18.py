from griptape.drivers import OpenAiAudioTranscriptionDriver
from griptape.engines import AudioTranscriptionEngine
from griptape.loaders import AudioLoader
from griptape.structures import Pipeline
from griptape.tasks import AudioTranscriptionTask
from griptape.utils import load_file

driver = OpenAiAudioTranscriptionDriver(model="whisper-1")

task = AudioTranscriptionTask(
    input=lambda _: AudioLoader().load(load_file("tests/resources/sentences2.wav")),
    audio_transcription_engine=AudioTranscriptionEngine(
        audio_transcription_driver=driver,
    ),
)

Pipeline(tasks=[task]).run()
