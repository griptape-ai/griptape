from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import RulesetsGenerationModule
from griptape.rules import Ruleset, Rule


class TestRulesetsGenerationModule:
    def test_run(self):
        module = RulesetsGenerationModule(rulesets=[Ruleset(name="test ruleset", rules=[Rule("test rule")])])

        assert "test rule" in module.run(RagContext(initial_query="test")).before_query[0]
