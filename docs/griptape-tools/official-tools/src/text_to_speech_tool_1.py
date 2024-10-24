import os

from griptape.drivers import ElevenLabsTextToSpeechDriver
from griptape.structures import Agent
from griptape.tools.text_to_speech.tool import TextToSpeechTool

driver = ElevenLabsTextToSpeechDriver(
    api_key=os.environ["ELEVEN_LABS_API_KEY"],
    model="eleven_multilingual_v2",
    voice="Matilda",
)

tool = TextToSpeechTool(
    text_to_speech_driver=driver,
)

Agent(tools=[tool]).run("Generate audio from this text: 'Hello, world!'")
