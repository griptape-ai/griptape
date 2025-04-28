from griptape.drivers.prompt.openai_chat_prompt_driver import OpenAiChatPromptDriver
from griptape.tasks import PromptTask

task = PromptTask(prompt_driver=OpenAiChatPromptDriver(model="gpt-4.1"))

task.run("Hello there!")
