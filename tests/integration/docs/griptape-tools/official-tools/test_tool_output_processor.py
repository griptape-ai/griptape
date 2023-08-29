class TestToolOutputProcessor:
    """
    https://docs.griptape.ai/en/latest/griptape-tools/official-tools/tool-output-processor/
    """

    def test_tool_output_processor(self):
        from griptape.structures import Agent
        from griptape.tools import ToolOutputProcessor
        from griptape.memory.tool import TextToolMemory

        text_memory = TextToolMemory(allowlist=[])

        Agent(tool_memory=text_memory, tools=[ToolOutputProcessor()])
