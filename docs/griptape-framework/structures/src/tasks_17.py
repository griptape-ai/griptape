import os

from griptape.drivers import ElevenLabsTextToSpeechDriver
from griptape.engines import TextToSpeechEngine
from griptape.structures import Pipeline
from griptape.tasks import TextToSpeechTask

driver = ElevenLabsTextToSpeechDriver(
    api_key=os.environ["ELEVEN_LABS_API_KEY"],
    model="eleven_multilingual_v2",
    voice="Matilda",
)

task = TextToSpeechTask(
    text_to_speech_engine=TextToSpeechEngine(
        text_to_speech_driver=driver,
    ),
)

Pipeline(tasks=[task]).run("Generate audio from this text: 'Hello, world!'")
