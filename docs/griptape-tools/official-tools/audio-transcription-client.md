# AudioTranscriptionClient

This Tool enables [Agents](../../griptape-framework/structures/agents.md) to transcribe speech from text using [Audio Transcription Engines](../../reference/griptape/engines/audio/audio_transcription_engine.md) and [Audio Transcription Drivers](../../reference/griptape/drivers/audio_transcription/index.md).

```python
from griptape.drivers import OpenAiAudioTranscriptionDriver
from griptape.engines import AudioTranscriptionEngine
from griptape.tools.audio_transcription_client.tool import AudioTranscriptionClient
from griptape.structures import Agent


driver = OpenAiAudioTranscriptionDriver(
    model="whisper-1"
)

tool = AudioTranscriptionClient(
    off_prompt=False,
    engine=AudioTranscriptionEngine(
        audio_transcription_driver=driver,
    ),
)

Agent(tools=[tool]).run("Transcribe the following audio file: /Users/andrew/code/griptape/tests/resources/sentences2.wav")
```