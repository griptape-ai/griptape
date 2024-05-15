## Overview

[Text to Speech Drivers](../../reference/griptape/drivers/text_to_speech/index.md) are used by [Text To Speech Engines](../engines/audio-engines.md) to build and execute API calls to audio generation models.

Provide a Driver when building an [Engine](../engines/audio-engines.md), then pass it to a [Tool](../tools/index.md) for use by an [Agent](../structures/agents.md):

### Eleven Labs

The [Eleven Labs Text to Speech Driver](../../reference/griptape/drivers/text_to_speech/elevenlabs_text_to_speech_driver.md) provides support for text-to-speech models hosted by Eleven Labs. This Driver supports configurations specific to Eleven Labs, like voice selection and output format.

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

## OpenAI

The [OpenAI Text to Speech Driver](../../reference/griptape/drivers/text_to_speech/openai_text_to_speech_driver.md) provides support for text-to-speech models hosted by OpenAI. This Driver supports configurations specific to OpenAI, like voice selection and output format.

```python
from griptape.drivers import OpenAiTextToSpeechDriver
from griptape.engines import TextToSpeechEngine
from griptape.tools.text_to_speech_client.tool import TextToSpeechClient
from griptape.structures import Agent

driver = OpenAiTextToSpeechDriver()

tool = TextToSpeechClient(
    engine=TextToSpeechEngine(
        text_to_speech_driver=driver,
    ),
)

Agent(tools=[tool]).run("Generate audio from this text: 'Hello, world!'")
```
