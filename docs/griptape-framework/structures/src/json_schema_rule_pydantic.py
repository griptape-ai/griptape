from __future__ import annotations

import pydantic

from griptape.rules.json_schema_rule import JsonSchemaRule
from griptape.structures import Agent


class SentimentModel(pydantic.BaseModel):
    answer: str
    relevant_emojis: list[str]


agent = Agent(rules=[JsonSchemaRule(SentimentModel.model_json_schema())])

output = agent.run("What is the sentiment of this message?: 'I am so happy!'").output

sentiment_analysis = SentimentModel.model_validate_json(output.value)

# Autocomplete via dot notation 🤩
print(sentiment_analysis.answer)
print(sentiment_analysis.relevant_emojis)
