from griptape.tools import Calculator


class TestCalculator:
    def test_calculate(self):
        assert Calculator(off_prompt=False).calculate({"values": {"expression": "5 * 5"}}).value == "25"
