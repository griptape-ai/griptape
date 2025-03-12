from griptape.tasks import PromptTask

task = PromptTask()

output = task.run("Hello there!")

print(output)
