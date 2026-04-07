from rich.pretty import pprint

from griptape.structures import Agent

agent = Agent()
agent.run("My name is Collin")

agent_dict = agent.to_dict(serializable_overrides={"max_meta_memory_entries": True, "id": False})
# `max_meta_memory_entries` will be included, `id` will not
pprint(agent_dict)
