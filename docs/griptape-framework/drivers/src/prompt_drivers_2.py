from griptape.common import PromptStack
from griptape.drivers import OpenAiChatPromptDriver

stack = PromptStack()

stack.add_system_message("You will be provided with Python code, and your task is to calculate its time complexity.")
stack.add_user_message(
    """
    def foo(n, k):
        accum = 0
        for i in range(n):
            for l in range(k):
                accum += i
        return accum
    """
)

result = OpenAiChatPromptDriver(model="gpt-3.5-turbo-16k", temperature=0).run(stack)

print(result.value)
