import pytest

from tests.utils.structure_tester import StructureTester


class TestCsvExtractionTask:
    @pytest.fixture(
        autouse=True,
        params=StructureTester.CSV_EXTRACTION_TASK_CAPABLE_PROMPT_DRIVERS,
        ids=StructureTester.prompt_driver_id_fn,
    )
    def structure_tester(self, request):
        from griptape.engines import CsvExtractionEngine
        from griptape.structures import Agent
        from griptape.tasks import ExtractionTask

        columns = ["Name", "Age", "Address"]

        # Create an agent and add the ExtractionTask to it
        agent = Agent(prompt_driver=request.param)
        agent.add_task(
            ExtractionTask(
                extraction_engine=CsvExtractionEngine(prompt_driver=request.param), args={"column_names": columns}
            )
        )

        return StructureTester(agent)

    def test_csv_extraction_task(self, structure_tester):
        structure_tester.run(
            """
            John (Age 25) lives at 123 Main St
            Jane (Age 30) lives at 456 Elm St
        """
        )
