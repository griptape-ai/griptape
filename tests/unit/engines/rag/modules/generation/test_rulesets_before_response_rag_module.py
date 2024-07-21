from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import RulesetsBeforeResponseRagModule
from griptape.rules import Rule, Ruleset


class TestRulesetsBeforeResponseRagModule:
    def test_run(self):
        module = RulesetsBeforeResponseRagModule(rulesets=[Ruleset(name="test ruleset", rules=[Rule("test rule")])])

        assert "test rule" in module.run(RagContext(query="test")).before_query[0]
