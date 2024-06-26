from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import RulesetsGenerationRagModule
from griptape.rules import Ruleset, Rule


class TestRulesetsGenerationRagModule:
    def test_run(self):
        module = RulesetsGenerationRagModule(rulesets=[Ruleset(name="test ruleset", rules=[Rule("test rule")])])

        assert "test rule" in module.run(RagContext(query="test")).before_query[0]
