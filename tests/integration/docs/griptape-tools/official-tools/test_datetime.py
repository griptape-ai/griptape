class TestCalculator:
    """
    https://docs.griptape.ai/en/latest/griptape-tools/official-tools/date-time/
    """

    def test_date_time_tool(self):
        from griptape.tools import DateTime

        date_time = DateTime()

        assert date_time is not None
