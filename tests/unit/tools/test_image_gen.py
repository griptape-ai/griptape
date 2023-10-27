from griptape.artifacts import ErrorArtifact
from griptape.tools import DalleImageGenerator


class TestDalleImageGenerator:
    def test_generator(self):
        tool = DalleImageGenerator()
        value = {"prompt": ""}
        assert isinstance(tool.dalle_generate({"values": value}), ErrorArtifact)
