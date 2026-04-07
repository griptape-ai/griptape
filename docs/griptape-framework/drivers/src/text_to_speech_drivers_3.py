import os

from griptape.drivers.text_to_speech.openai import AzureOpenAiTextToSpeechDriver
from griptape.structures import Agent
from griptape.tools.text_to_speech.tool import TextToSpeechTool

driver = AzureOpenAiTextToSpeechDriver(
    api_key=os.environ["AZURE_OPENAI_API_KEY_4"],
    model="tts",
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT_4"],
)

tool = TextToSpeechTool(
    text_to_speech_driver=driver,
)

Agent(tools=[tool]).run("Generate audio from this text: 'Hello, world!'")
