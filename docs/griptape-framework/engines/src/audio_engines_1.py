import os

from griptape.drivers import ElevenLabsTextToSpeechDriver
from griptape.engines import TextToSpeechEngine

driver = ElevenLabsTextToSpeechDriver(
    api_key=os.environ["ELEVEN_LABS_API_KEY"],
    model="eleven_multilingual_v2",
    voice="Laura",
)

engine = TextToSpeechEngine(
    text_to_speech_driver=driver,
)

engine.run(
    prompts=["Hello, world!"],
)
