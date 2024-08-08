import os

from griptape.drivers import ElevenLabsTextToSpeechDriver
from griptape.engines import TextToSpeechEngine
from griptape.structures import Agent
from griptape.tools.text_to_speech_client.tool import TextToSpeechClient

driver = ElevenLabsTextToSpeechDriver(
    api_key=os.environ["ELEVEN_LABS_API_KEY"],
    model="eleven_multilingual_v2",
    voice="Matilda",
)

tool = TextToSpeechClient(
    engine=TextToSpeechEngine(
        text_to_speech_driver=driver,
    ),
)

Agent(tools=[tool]).run("Generate audio from this text: 'Hello, world!'")
