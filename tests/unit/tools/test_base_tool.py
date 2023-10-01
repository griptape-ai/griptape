import inspect
import os
import pytest
import yaml
from schema import SchemaMissingKeyError
from griptape.drivers import LocalVectorStoreDriver
from griptape.engines import VectorQueryEngine
from griptape.memory.tool import ToolMemory
from griptape.engines import VectorQueryEngine, PromptSummaryEngine
from griptape.tasks import ActionSubtask
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver
from tests.mocks.mock_tool.tool import MockTool


class TestBaseTool:
    @pytest.fixture
    def tool(self):
        return MockTool(
            test_field="hello",
            test_int=5,
            test_dict={"foo": "bar"}
        )

    def test_manifest_path(self, tool):
        assert tool.manifest_path == os.path.join(tool.abs_dir_path, tool.MANIFEST_FILE)

    def test_requirements_path(self, tool):
        assert tool.requirements_path == os.path.join(tool.abs_dir_path, tool.REQUIREMENTS_FILE)

    def test_manifest(self, tool):
        with open(tool.manifest_path, "r") as yaml_file:
            assert tool.manifest == yaml.safe_load(yaml_file)

    def test_abs_file_path(self, tool):
        assert tool.abs_file_path == os.path.abspath(inspect.getfile(tool.__class__))

    def test_abs_dir_path(self, tool):
        assert tool.abs_dir_path == os.path.dirname(tool.abs_file_path)

    def test_name(self):
        assert MockTool().name == "MockTool"
        assert MockTool(name="FooBar").name == "FooBar"

    def test_class_name(self):
        assert MockTool().class_name == "MockTool"
        assert MockTool(name="FooBar").class_name == "MockTool"

    def test_validate(self, tool):
        assert tool.validate()

    def test_invalid_config(self):
        try:
            from tests.mocks.invalid_mock_tool.tool import InvalidMockTool

            assert False
        except SchemaMissingKeyError as e:
            assert True

    def test_memory(self):
        query_engine = VectorQueryEngine(
            vector_store_driver=LocalVectorStoreDriver(
                embedding_driver=MockEmbeddingDriver()
            )
        )

        tool = MockTool(
            output_memory={
                "test": [
                    ToolMemory(name="Memory1", query_engine=query_engine, summary_engine=PromptSummaryEngine()),
                    ToolMemory(name="Memory2", query_engine=query_engine, summary_engine=PromptSummaryEngine())
                ]
            }
        )

        assert len(tool.output_memory["test"]) == 2

    def test_memory_validation(self):
        query_engine = VectorQueryEngine(
            vector_store_driver=LocalVectorStoreDriver(
                embedding_driver=MockEmbeddingDriver()
            )
        )

        with pytest.raises(ValueError):
            MockTool(
                output_memory={
                    "test": [
                        ToolMemory(name="Memory1", query_engine=query_engine, summary_engine=PromptSummaryEngine()),
                        ToolMemory(name="Memory1", query_engine=query_engine, summary_engine=PromptSummaryEngine())
                    ]
                }
            )

        with pytest.raises(ValueError):
            MockTool(
                output_memory={
                    "output_memory": [
                        ToolMemory(name="Memory1", query_engine=query_engine, summary_engine=PromptSummaryEngine())
                    ]
                }
            )

        assert MockTool(
                output_memory={
                    "test": [
                        ToolMemory(
                            name="Memory1", query_engine=query_engine, summary_engine=PromptSummaryEngine()
                        )
                    ],
                    "test_str_output": [
                        ToolMemory(
                            name="Memory1", query_engine=query_engine, summary_engine=PromptSummaryEngine()
                        )
                    ]
                }
            )

    def test_find_input_memory(self):
        query_engine = VectorQueryEngine(
            vector_store_driver=LocalVectorStoreDriver(
                embedding_driver=MockEmbeddingDriver()
            )
        )

        assert MockTool().find_input_memory("foo") is None
        assert MockTool(input_memory=[ToolMemory(name="foo")]).find_input_memory("foo") is not None
        assert MockTool(input_memory=[
            ToolMemory(name="foo", query_engine=query_engine, summary_engine=PromptSummaryEngine())
        ]).find_input_memory("foo") is not None

    def test_execute(self, tool):
        assert tool.execute(
            tool.test_list_output,
            ActionSubtask("foo")
        ).to_text() == "foo\n\nbar"
