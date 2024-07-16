import pytest

from tests.utils.structure_tester import StructureTester


class TestRule:
    @pytest.fixture(
        autouse=True, params=StructureTester.RULE_CAPABLE_PROMPT_DRIVERS, ids=StructureTester.prompt_driver_id_fn
    )
    def structure_tester(self, request):
        from griptape.rules import Rule
        from griptape.structures import Agent

        agent = Agent(prompt_driver=request.param, rules=[Rule("Your name is Tony.")])

        return StructureTester(agent)

    def test_rule(self, structure_tester):
        structure_tester.run("What is your name?")
