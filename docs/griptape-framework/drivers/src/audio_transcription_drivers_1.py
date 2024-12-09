from griptape.drivers import OpenAiAudioTranscriptionDriver
from griptape.structures import Agent
from griptape.tools.audio_transcription.tool import AudioTranscriptionTool

driver = OpenAiAudioTranscriptionDriver(model="whisper-1")

tool = AudioTranscriptionTool(
    off_prompt=False,
    audio_transcription_driver=driver,
)

Agent(tools=[tool]).run("Transcribe the following audio file: tests/resources/sentences.wav")
