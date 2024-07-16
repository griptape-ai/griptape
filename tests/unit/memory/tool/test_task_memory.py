import pytest

from griptape.artifacts import BlobArtifact, CsvRowArtifact, ErrorArtifact, InfoArtifact, ListArtifact, TextArtifact
from griptape.memory import TaskMemory
from griptape.memory.task.storage import BlobArtifactStorage, TextArtifactStorage
from griptape.structures import Agent
from griptape.tasks import ActionsSubtask
from tests.mocks.mock_tool.tool import MockTool
from tests.utils import defaults


class TestTaskMemory:
    @pytest.fixture(autouse=True)
    def _mock_griptape(self, mocker):
        mocker.patch("griptape.engines.CsvExtractionEngine.extract", return_value=[CsvRowArtifact({"foo": "bar"})])

    @pytest.fixture()
    def memory(self):
        return defaults.text_task_memory("MyMemory")

    def test_init(self, memory):
        assert memory.name == "MyMemory"

    def test_validate_artifact_storages(self):
        with pytest.raises(ValueError):
            TaskMemory(artifact_storages={TextArtifact: BlobArtifactStorage(), BlobArtifact: BlobArtifactStorage()})

    def test_get_memory_driver_for(self, memory):
        assert isinstance(memory.get_storage_for(TextArtifact("foo")), TextArtifactStorage)
        assert isinstance(memory.get_storage_for(BlobArtifact(b"foo")), BlobArtifactStorage)

    def test_store_artifact(self, memory):
        assert memory.store_artifact("test", TextArtifact("foo1")) is None
        assert memory.store_artifact("test", TextArtifact("foo2")) is None
        assert isinstance(memory.store_artifact("test", BlobArtifact(b"foo3")), ErrorArtifact)
        assert memory.store_artifact("btest", BlobArtifact(b"foo4")) is None
        assert isinstance(memory.store_artifact("btest", TextArtifact("foo5")), ErrorArtifact)
        assert isinstance(memory.store_artifact("test", InfoArtifact("foo1")), InfoArtifact)
        assert memory.store_artifact("test", InfoArtifact("foo1", name="foobar")).name == "foobar"
        assert memory.store_artifact("test", ListArtifact([TextArtifact("foo1")])) is None

    def test_find_input_memory(self, memory):
        assert memory.find_input_memory(memory.name) == memory

    def test_process_output(self, memory):
        artifact = TextArtifact("foo")
        subtask = ActionsSubtask()

        subtask.structure = Agent()

        output = memory.process_output(MockTool().test, subtask, artifact)

        entries = subtask.structure.meta_memory.entries

        assert len(entries) == 1
        assert entries[0].actions == "[]"
        assert entries[0].answer.startswith(
            'Output of "MockTool.test" was stored in memory with memory_name "MyMemory"'
        )
        assert entries[0].thought is None

        assert output.to_text().startswith('Output of "MockTool.test" was stored in memory')
        assert memory.namespace_metadata[artifact.id] == subtask.actions_to_json()

    def test_process_output_with_many_artifacts(self, memory):
        assert (
            memory.process_output(MockTool().test, ActionsSubtask(), ListArtifact([TextArtifact("foo")]))
            .to_text()
            .startswith('Output of "MockTool.test" was stored in memory')
        )

    def test_load_artifacts_for_text_artifact(self, memory):
        memory.process_output(MockTool().test, ActionsSubtask(), TextArtifact("foo", name="test"))

        assert len(memory.load_artifacts("test")) == 1

    def test_load_artifacts_for_blob_artifact(self, memory):
        memory.process_output(MockTool().test, ActionsSubtask(), BlobArtifact(b"foo", name="test"))

        assert len(memory.load_artifacts("test")) == 1

    def test_load_artifacts_for_text_list_artifact(self, memory):
        memory.process_output(
            MockTool().test,
            ActionsSubtask(),
            ListArtifact([TextArtifact("foo1", name="test1"), TextArtifact("foo2", name="test2")], name="test"),
        )

        assert len(memory.load_artifacts("test")) == 2

    def test_load_artifacts_for_blob_list_artifact(self, memory):
        memory.process_output(
            MockTool().test,
            ActionsSubtask(),
            ListArtifact([BlobArtifact(b"foo", name="test1"), BlobArtifact(b"foo", name="test2")], name="test"),
        )

        assert len(memory.load_artifacts("test")) == 2

    def test_summarize_namespace(self, memory):
        memory.store_artifact("foo", TextArtifact("test"))

        assert memory.summarize_namespace("foo").value == "mock output"

    def test_query_namespace(self, memory):
        memory.store_artifact("foo", TextArtifact("test"))

        assert memory.query_namespace("foo", "query").value == "mock output"
