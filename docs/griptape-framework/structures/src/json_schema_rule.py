import json

import schema

from griptape.rules.json_schema_rule import JsonSchemaRule
from griptape.structures import Agent

agent = Agent(
    rules=[
        JsonSchemaRule(
            schema.Schema({"answer": str, "relevant_emojis": schema.Schema(["str"])}).json_schema("Output Format")
        )
    ]
)

output = agent.run("What is the sentiment of this message?: 'I am so happy!'").output

print(json.dumps(json.loads(output.value), indent=2))
