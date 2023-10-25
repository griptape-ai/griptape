from griptape.tools import Calculator


class TestCalculator:
    def test_calculate(self):
        assert (
            Calculator().calculate({"values": {"expression": "5 * 5"}}).value
            == "25"
        )
