from griptape.structures import Agent

agent = Agent()
agent.run("My name is Collin")

agent_dict = agent.to_dict()

new_agent = Agent.from_dict(agent_dict)

new_agent.run("What's my name?")
