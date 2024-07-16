import pytest

from griptape.drivers.structure_run.local_structure_run_driver import LocalStructureRunDriver
from griptape.structures import Agent
from griptape.tools import StructureRunClient
from tests.mocks.mock_prompt_driver import MockPromptDriver


class TestStructureRunClient:
    @pytest.fixture()
    def client(self):
        driver = MockPromptDriver()
        agent = Agent(prompt_driver=driver)

        return StructureRunClient(
            description="foo bar", driver=LocalStructureRunDriver(structure_factory_fn=lambda: agent)
        )

    def test_run_structure(self, client):
        assert client.run_structure({"values": {"args": "foo bar"}}).value == "mock output"
        assert client.description == "foo bar"
