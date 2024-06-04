# TextToSpeechClient

This Tool enables LLMs to synthesize speech from text using [Text to Speech Engines](../../reference/griptape/engines/audio/text_to_speech_engine.md) and [Text to Speech Drivers](../../reference/griptape/drivers/text_to_speech/index.md).

```python
import os

from griptape.drivers import ElevenLabsTextToSpeechDriver
from griptape.engines import TextToSpeechEngine
from griptape.tools.text_to_speech_client.tool import TextToSpeechClient
from griptape.structures import Agent


driver = ElevenLabsTextToSpeechDriver(
    api_key=os.getenv("ELEVEN_LABS_API_KEY"),
    model="eleven_multilingual_v2",
    voice="Matilda",
)

tool = TextToSpeechClient(
    engine=TextToSpeechEngine(
        text_to_speech_driver=driver,
    ),
)

Agent(tools=[tool]).run("Generate audio from this text: 'Hello, world!'")
```