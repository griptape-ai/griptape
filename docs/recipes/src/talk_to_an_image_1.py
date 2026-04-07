import os

import requests

from griptape.drivers.file_manager.local import LocalFileManagerDriver
from griptape.drivers.prompt.openai import OpenAiChatPromptDriver
from griptape.loaders import ImageLoader
from griptape.structures import Agent
from griptape.tools import FileManagerTool, ImageQueryTool

# Create the images directory if it doesn't exist
images_dir = f"{os.getcwd()}/images"
os.makedirs(images_dir, exist_ok=True)

# Download an image from the web
image_url = "https://picsum.photos/200/300"
image_path = f"{images_dir}/image.jpg"
response = requests.get(image_url)
with open(image_path, "wb") as file:
    file.write(response.content)

driver = LocalFileManagerDriver(workdir=images_dir)
agent = Agent(
    tools=[
        FileManagerTool(file_manager_driver=driver),
        ImageQueryTool(
            prompt_driver=OpenAiChatPromptDriver(model="gpt-4.1"), image_loader=ImageLoader(file_manager_driver=driver)
        ),
    ]
)

agent.run("What files are in the current directory?")
agent.run("What is in the file image.jpg?")
