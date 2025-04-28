from griptape.drivers.prompt.openai_chat_prompt_driver import OpenAiChatPromptDriver
from griptape.rules import Rule, Ruleset
from griptape.tasks import PromptTask

task = PromptTask(
    input="You are speaking to: {{ user_name }}. User said: {{ args[0] }}",
    prompt_driver=OpenAiChatPromptDriver(model="gpt-4.1"),
    context={"user_name": "Collin"},
    rulesets=[
        Ruleset(
            name="Backstory",
            rules=[
                Rule("Your name is Oswald."),
            ],
        ),
        Ruleset(
            name="Behavior",
            rules=[
                Rule("Introduce yourself at the start of the conversation."),
            ],
        ),
    ],
)

task.run("Hi there!")
