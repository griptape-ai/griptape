import pytest
from griptape.drivers.structure_run.local_structure_run_driver import LocalStructureRunDriver
from griptape.tools import GriptapeStructureRunClient
from griptape.structures import Agent
from tests.mocks.mock_prompt_driver import MockPromptDriver


class TestGriptapeStructureRunClient:
    @pytest.fixture
    def client(self):
        driver = MockPromptDriver()
        agent = Agent(prompt_driver=driver)

        return GriptapeStructureRunClient(description="foo bar", driver=LocalStructureRunDriver(structure=agent))

    def test_run_structure(self, client):
        assert client.run_structure({"values": {"args": "foo bar"}}).value == "mock output"
        assert client.description == "foo bar"
