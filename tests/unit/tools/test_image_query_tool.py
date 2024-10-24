import pytest

from griptape.artifacts.image_artifact import ImageArtifact
from griptape.tools import ImageQueryTool
from tests.mocks.mock_image_query_driver import MockImageQueryDriver
from tests.utils import defaults


class TestImageQueryTool:
    @pytest.fixture()
    def tool(self):
        task_memory = defaults.text_task_memory("memory_name")
        task_memory.store_artifact("namespace", ImageArtifact(b"", format="png", width=1, height=1, name="test"))
        return ImageQueryTool(input_memory=[task_memory], image_query_driver=MockImageQueryDriver())

    def test_query_image_from_disk(self, tool):
        assert tool.query_image_from_disk({"values": {"query": "test", "image_paths": []}}).value == "mock text"

    def test_query_images_from_memory(self, tool):
        assert (
            tool.query_images_from_memory(
                {
                    "values": {
                        "query": "test",
                        "memory_name": tool.input_memory[0].name,
                        "image_artifacts": [
                            {
                                "image_artifact_name": "test",
                                "image_artifact_namespace": "namespace",
                            }
                        ],
                    }
                }
            ).value
            == "mock text"
        )
