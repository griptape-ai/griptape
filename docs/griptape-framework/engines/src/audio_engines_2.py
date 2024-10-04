from griptape.drivers import OpenAiAudioTranscriptionDriver
from griptape.engines import AudioTranscriptionEngine
from griptape.loaders import AudioLoader

driver = OpenAiAudioTranscriptionDriver(model="whisper-1")

engine = AudioTranscriptionEngine(
    audio_transcription_driver=driver,
)

audio_artifact = AudioLoader().load("tests/resources/sentences.wav")
engine.run(audio_artifact)
