import pytest

from griptape.tools import Computer
from tests.mocks.docker.fake_api_client import make_fake_client


class TestComputer:
    @pytest.fixture()
    def computer(self):
        return Computer(docker_client=make_fake_client(), install_dependencies_on_init=False)

    def test_execute_code(self, computer):
        assert computer.execute_code({"values": {"code": "print(1)", "filename": "foo.py"}}).value == "hello world"

    def test_execute_command(self, computer):
        assert computer.execute_command({"values": {"command": "ls"}}).value == "hello world"
