class TestConversationMemory:
    """
    https://docs.griptape.ai/en/latest/griptape-framework/structures/conversation-memory/
    """

    def test_conversation_memory(self):
        from griptape.structures import Pipeline
        from griptape.memory.structure import ConversationMemory

        pipeline = Pipeline(memory=ConversationMemory())

        assert pipeline is not None

    def test_buffer_conversation_memory(self):
        from griptape.structures import Pipeline
        from griptape.memory.structure import BufferConversationMemory

        pipeline = Pipeline(memory=BufferConversationMemory(buffer_size=3))

        assert pipeline is not None

    def test_summary_conversation_memory(self):
        from griptape.structures import Pipeline
        from griptape.memory.structure import SummaryConversationMemory

        pipeline = Pipeline(memory=SummaryConversationMemory(offset=2))

        assert pipeline is not None

    def test_local_conversation_memory_driver(self):
        from griptape.drivers import LocalConversationMemoryDriver
        from griptape.memory.structure import ConversationMemory

        memory = ConversationMemory(
            driver=LocalConversationMemoryDriver(file_path="memory.json")
        )

        assert memory is not None

    def test_load_local_conversation_memory_driver(self):
        from griptape.drivers import LocalConversationMemoryDriver

        memory = LocalConversationMemoryDriver(file_path="memory.json").load()

        assert memory is None
