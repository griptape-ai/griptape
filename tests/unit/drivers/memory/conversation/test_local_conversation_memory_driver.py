import contextlib
import os
from pathlib import Path

import pytest

from griptape.drivers import LocalConversationMemoryDriver
from griptape.memory.structure import ConversationMemory
from griptape.structures import Pipeline
from griptape.tasks import PromptTask


class TestLocalConversationMemoryDriver:
    MEMORY_FILE_PATH = "test_memory.json"

    @pytest.fixture(autouse=True)
    def _run_before_and_after_tests(self):
        self.__delete_file(self.MEMORY_FILE_PATH)

        yield

        self.__delete_file(self.MEMORY_FILE_PATH)

    def test_store(self):
        memory_driver = LocalConversationMemoryDriver(persist_file=self.MEMORY_FILE_PATH)
        memory = ConversationMemory(conversation_memory_driver=memory_driver, autoload=False)
        pipeline = Pipeline(conversation_memory=memory)

        pipeline.add_task(PromptTask("test"))

        assert not os.path.exists(self.MEMORY_FILE_PATH)

        pipeline.run()

        assert os.path.exists(self.MEMORY_FILE_PATH)

    def test_load(self):
        memory_driver = LocalConversationMemoryDriver(persist_file=self.MEMORY_FILE_PATH)
        memory = ConversationMemory(
            conversation_memory_driver=memory_driver, autoload=False, max_runs=5, meta={"foo": "bar"}
        )
        pipeline = Pipeline(conversation_memory=memory)

        pipeline.add_task(PromptTask("test"))

        pipeline.run()
        pipeline.run()

        runs, metadata = memory_driver.load()

        assert len(runs) == 2
        assert runs[0].input.value == "test"
        assert runs[0].output.value == "mock output"
        assert metadata == {"foo": "bar"}

        runs[0].input.value = "new test"

    def test_load_bad_data(self):
        Path(self.MEMORY_FILE_PATH).write_text("bad data")
        memory_driver = LocalConversationMemoryDriver(persist_file=self.MEMORY_FILE_PATH)

        with pytest.raises(ValueError, match="Unable to load data from test_memory.json"):
            ConversationMemory(conversation_memory_driver=memory_driver)

    def test_autoload(self):
        memory_driver = LocalConversationMemoryDriver(persist_file=self.MEMORY_FILE_PATH)
        memory = ConversationMemory(conversation_memory_driver=memory_driver, autoload=False)
        pipeline = Pipeline(conversation_memory=memory)

        pipeline.add_task(PromptTask("test"))

        pipeline.run()
        pipeline.run()

        autoloaded_memory = ConversationMemory(conversation_memory_driver=memory_driver)

        assert autoloaded_memory.type == "ConversationMemory"
        assert len(autoloaded_memory.runs) == 2
        assert autoloaded_memory.runs[0].input.value == "test"
        assert autoloaded_memory.runs[0].output.value == "mock output"

    def __delete_file(self, persist_file) -> None:
        with contextlib.suppress(FileNotFoundError):
            os.remove(persist_file)
