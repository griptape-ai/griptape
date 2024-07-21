import pytest

from tests.utils.structure_tester import StructureTester


class TestJsonExtractionTask:
    @pytest.fixture(
        autouse=True,
        params=StructureTester.JSON_EXTRACTION_TASK_CAPABLE_PROMPT_DRIVERS,
        ids=StructureTester.prompt_driver_id_fn,
    )
    def structure_tester(self, request):
        from schema import Schema

        from griptape.engines import JsonExtractionEngine
        from griptape.structures import Agent
        from griptape.tasks import ExtractionTask

        # Define some JSON data
        user_schema = Schema({"users": [{"name": str, "age": int, "location": str}]}).json_schema("UserSchema")

        agent = Agent(prompt_driver=request.param)
        agent.add_task(
            ExtractionTask(
                extraction_engine=JsonExtractionEngine(prompt_driver=request.param),
                args={"template_schema": user_schema},
            )
        )

        return StructureTester(agent)

    def test_json_extraction_task(self, structure_tester):
        structure_tester.run(
            """
            John (Age 25) lives at 123 Main St
            Jane (Age 30) lives at 456 Elm St
        """
        )
