from tests.utils.structure_runner import StructureRunner
import pytest


class TestFileManager:
    @pytest.fixture(
        autouse=True,
        params=StructureRunner.TOOLKIT_TASK_CAPABLE_PROMPT_DRIVERS,
        ids=StructureRunner.prompt_driver_id_fn,
    )
    def structure_runner(self, request):
        from griptape.structures import Agent
        from griptape.tools import FileManager

        return StructureRunner(Agent(tools=[FileManager()], conversation_memory=None, prompt_driver=request.param))

    def test_save_content_to_disk(self, structure_runner):
        structure_runner.run_structure('Write the content "Hello World!" to a file called "poem.txt".')

        structure_runner.run_structure('Write the content "Hello World!" to a file called ".".')

    def test_load_files_from_disk(self, structure_runner):
        structure_runner.run_structure("Read the content of the file called 'poem.txt'.")
