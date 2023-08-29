class TestCalculator:
    """
    https://docs.griptape.ai/en/latest/griptape-tools/official-tools/calculator/
    """

    def test_calculator_tool(self):
        from griptape.tools import Calculator

        calculator = Calculator()

        assert calculator is not None

        
