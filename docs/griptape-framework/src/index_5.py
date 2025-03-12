from griptape.drivers.prompt.openai_chat_prompt_driver import OpenAiChatPromptDriver
from griptape.tasks import PromptTask

task = PromptTask(
    input="You are speaking to: {{ user_name }}. User said: {{ args[0] }}",
    prompt_driver=OpenAiChatPromptDriver(model="gpt-4o"),
    context={"user_name": "Collin"},
)

task.run("Hi there!")
