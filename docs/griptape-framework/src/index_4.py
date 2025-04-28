from griptape.drivers.prompt.openai_chat_prompt_driver import OpenAiChatPromptDriver
from griptape.tasks import PromptTask

task = PromptTask(
    input="User said: {{ args[0] }}",
    prompt_driver=OpenAiChatPromptDriver(model="gpt-4.1"),
)

task.run("Hi there!")
