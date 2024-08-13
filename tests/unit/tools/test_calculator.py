from griptape.tools import CalculatorTool


class TestCalculator:
    def test_calculate(self):
        assert CalculatorTool().calculate({"values": {"expression": "5 * 5"}}).value == "25"
