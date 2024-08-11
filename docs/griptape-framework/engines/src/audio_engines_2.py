from griptape.drivers import OpenAiAudioTranscriptionDriver
from griptape.engines import AudioTranscriptionEngine
from griptape.loaders import AudioLoader
from griptape.utils import load_file

driver = OpenAiAudioTranscriptionDriver(model="whisper-1")

engine = AudioTranscriptionEngine(
    audio_transcription_driver=driver,
)

audio_artifact = AudioLoader().load(load_file("tests/resources/sentences.wav"))
engine.run(audio_artifact)
