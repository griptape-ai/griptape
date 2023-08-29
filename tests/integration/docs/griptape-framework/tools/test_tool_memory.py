class TestToolMemory:
    """
    https://docs.griptape.ai/en/latest/griptape-framework/tools/tool-memory/
    """

    def test_tool_memory(self):
        from griptape.memory.tool import TextToolMemory, BlobToolMemory
        from griptape.structures import Agent
        from griptape.tools import WebScraper, FileManager, ToolOutputProcessor

        """
        Define tool memory for storing textual and
        non-textual content.
        """
        text_memory = TextToolMemory(
            # Disable all memory activities, so we can use
            # ToolOutputProcessor as a tool later.
            allowlist=[]
        )
        blob_memory = BlobToolMemory()

        """
        WebScraper enables LLMs to web pages.

        Here we wrap WebScraper's `get_content` activity
        in the text memory. Any result from this
        activity will be stored in that memory and the result
        ID will be returned to the LLM.
        """
        web_scraper = WebScraper(output_memory={"get_content": [text_memory]})

        """
        FileManager enables LLMs to store and load files from disk.

        Here we set input_memory for tool activities to pull data from and
        wrap the `load_files_from_disk` activity output with the blob memory.
        """
        file_manager = FileManager(
            input_memory=[text_memory],
            output_memory={"load_files_from_disk": [blob_memory]},
        )

        """
        ToolOutputProcessor enables LLMs to browse, extract, and query text memory.
        """
        memory_browser = ToolOutputProcessor(input_memory=[text_memory])

        agent = Agent(tools=[web_scraper, file_manager, memory_browser])

        result = agent.run(
            "Load https://www.griptape.ai, summarize it, "
            "and store it in griptape.txt"
        )

        assert result.output is not None
