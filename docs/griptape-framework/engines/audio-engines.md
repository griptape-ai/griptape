## Overview

[Audio Generation Engines](../../reference/griptape/engines/audio/index.md) facilitate audio generation. Audio Generation Engines provides a `run` method that accepts the necessary inputs for its particular mode and provides the request to the configured [Driver](../drivers/text-to-speech-drivers.md).

### Text to Speech

This Engine facilitates synthesizing speech from text inputs.

```python
import os

from griptape.drivers import ElevenLabsTextToSpeechDriver
from griptape.engines import TextToSpeechEngine


driver = ElevenLabsTextToSpeechDriver(
    api_key=os.getenv("ELEVEN_LABS_API_KEY"),
    model="eleven_multilingual_v2",
    voice="Rachel",
)

engine = TextToSpeechEngine(
    text_to_speech_driver=driver,
)

engine.run(
    prompts=["Hello, world!"],
)
```

### Audio Transcription

The [Audio Transcription Engine](../../reference/griptape/engines/audio/audio_transcription_engine.md) facilitates transcribing speech from audio inputs.

```python
from griptape.drivers import OpenAiAudioTranscriptionDriver
from griptape.engines import AudioTranscriptionEngine
from griptape.loaders import AudioLoader
from griptape.utils import load_file


driver = OpenAiAudioTranscriptionDriver(
    model="whisper-1"
)

engine = AudioTranscriptionEngine(
    audio_transcription_driver=driver,
)

audio_artifact = AudioLoader().load(load_file("tests/resources/sentences.wav"))
engine.run(audio_artifact)
```
