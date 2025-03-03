from rich.pretty import pprint

from griptape.tools import CalculatorTool

tool = CalculatorTool()

pprint(tool.to_activity_json_schema(tool.calculate, "Calculate Schema"))
