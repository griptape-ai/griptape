from griptape.memory.structure import ConversationMemory
from griptape.structures import Agent

conversation_memory = ConversationMemory(max_runs=2)
agent = Agent(conversation_memory=conversation_memory)

agent.run("Run 1")
agent.run("Run 2")
agent.run("Run 3")
agent.run("Run 4")
agent.run("Run 5")

print(conversation_memory.runs[0].input == "run4")
print(conversation_memory.runs[1].input == "run5")
