# Rulesets

A [Ruleset can be created](https://cloud.griptape.ai/rulesets/create) to store sets of rules and pull them in dynamically for faster iteration on LLM behavior in a deployed environment. A Ruleset takes a list of [Rules](https://cloud.griptape.ai/rules/create). A Ruleset can be given an `alias` so it can be referenced by a user-provided unique identifier:

```bash
export GT_CLOUD_API_KEY=<your API key here>
export ALIAS=<your ruleset alias>
curl -H "Authorization: Bearer ${GT_CLOUD_API_KEY}" https://cloud.griptape.ai/api/rulesets?alias=${ALIAS}
```
