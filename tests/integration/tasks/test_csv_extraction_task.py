from tests.utils.structure_tester import StructureTester
import pytest


class TestCsvExtractionTask:
    @pytest.fixture(
        autouse=True,
        params=StructureTester.CSV_EXTRACTION_TASK_CAPABLE_PROMPT_DRIVERS,
        ids=StructureTester.prompt_driver_id_fn,
    )
    def structure_tester(self, request):
        from griptape.tasks import ExtractionTask
        from griptape.structures import Agent
        from griptape.engines import CsvExtractionEngine

        # Instantiate the CSV extraction engine
        csv_extraction_engine = CsvExtractionEngine()

        columns = ["Name", "Age", "Address"]

        # Create an agent and add the ExtractionTask to it
        agent = Agent(prompt_driver=request.param)
        agent.add_task(ExtractionTask(extraction_engine=csv_extraction_engine, args={"column_names": columns}))

        return StructureTester(agent)

    def test_json_extraction_task(self, structure_tester):
        structure_tester.run(
            """
            Here is some CSV data:
        Name, Age, Address
        John, 25, 123 Main St
        Jane, 30, 456 Elm St
        """
        )
