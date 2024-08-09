from griptape.drivers import OpenAiAudioTranscriptionDriver
from griptape.engines import AudioTranscriptionEngine
from griptape.structures import Agent
from griptape.tools.audio_transcription_client.tool import AudioTranscriptionClient

driver = OpenAiAudioTranscriptionDriver(model="whisper-1")

tool = AudioTranscriptionClient(
    off_prompt=False,
    engine=AudioTranscriptionEngine(
        audio_transcription_driver=driver,
    ),
)

Agent(tools=[tool]).run("Transcribe the following audio file: tests/resources/sentences.wav")
