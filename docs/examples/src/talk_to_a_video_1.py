import time

import google.generativeai as genai

from griptape.artifacts import GenericArtifact, TextArtifact
from griptape.config import GoogleStructureConfig
from griptape.structures import Agent

video_file = genai.upload_file(path="tests/resources/griptape-comfyui.mp4")
while video_file.state.name == "PROCESSING":
    time.sleep(2)
    video_file = genai.get_file(video_file.name)

if video_file.state.name == "FAILED":
    raise ValueError(video_file.state.name)

agent = Agent(
    config=GoogleStructureConfig(),
    input=[
        GenericArtifact(video_file),
        TextArtifact("Answer this question regarding the video: {{ args[0] }}"),
    ],
)

agent.run("Are there any scenes that show a character with earings?")
agent.run("What happens in the scene starting at 19 seconds?")
