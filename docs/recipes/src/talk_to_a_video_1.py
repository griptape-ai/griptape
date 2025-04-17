import time

from griptape.artifacts import GenericArtifact, TextArtifact
from griptape.configs import Defaults
from griptape.configs.drivers import GoogleDriversConfig
from griptape.structures import Agent

Defaults.drivers_config = GoogleDriversConfig()
client = Defaults.drivers_config.prompt_driver.client

video_file = client.files.upload(file="tests/resources/griptape-comfyui.mp4")
while video_file.state and video_file.state.name == "PROCESSING":
    time.sleep(2)
    if video_file.name:
        video_file = client.files.get(name=video_file.name)

if video_file.state and video_file.state.name == "FAILED":
    raise ValueError(video_file.state.name)

agent = Agent(
    input=[
        GenericArtifact(video_file),
        TextArtifact("Answer this question regarding the video: {{ args[0] }}"),
    ]
)

agent.run("Are there any scenes that show a character with earings?")
agent.run("What happens in the scene starting at 19 seconds?")
