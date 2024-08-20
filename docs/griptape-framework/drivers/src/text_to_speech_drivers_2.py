from griptape.drivers import OpenAiTextToSpeechDriver
from griptape.engines import TextToSpeechEngine
from griptape.structures import Agent
from griptape.tools.text_to_speech.tool import TextToSpeechTool

driver = OpenAiTextToSpeechDriver()

tool = TextToSpeechTool(
    engine=TextToSpeechEngine(
        text_to_speech_driver=driver,
    ),
)

Agent(tools=[tool]).run("Generate audio from this text: 'Hello, world!'")
