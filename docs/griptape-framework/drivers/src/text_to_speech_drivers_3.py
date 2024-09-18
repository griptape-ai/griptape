import os

from griptape.drivers import AzureOpenAiTextToSpeechDriver
from griptape.engines import TextToSpeechEngine
from griptape.structures import Agent
from griptape.tools.text_to_speech.tool import TextToSpeechTool

driver = AzureOpenAiTextToSpeechDriver(
    api_key=os.environ["AZURE_OPENAI_API_KEY_4"],
    model="tts",
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT_4"],
)

tool = TextToSpeechTool(
    engine=TextToSpeechEngine(
        text_to_speech_driver=driver,
    ),
)

Agent(tools=[tool]).run("Generate audio from this text: 'Hello, world!'")
