import pytest

from griptape.drivers.structure_run.local_structure_run_driver import LocalStructureRunDriver
from griptape.structures import Agent
from griptape.tools import StructureRunTool


class TestStructureRunTool:
    @pytest.fixture()
    def client(self):
        agent = Agent()

        return StructureRunTool(
            description="foo bar", structure_run_driver=LocalStructureRunDriver(create_structure=lambda: agent)
        )

    def test_run_structure(self, client):
        assert client.run_structure({"values": {"args": "foo bar"}}).value == "mock output"
        assert client.description == "foo bar"
