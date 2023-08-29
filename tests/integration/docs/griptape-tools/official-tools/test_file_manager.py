class TestFileManager:
    """
    https://docs.griptape.ai/en/latest/griptape-tools/official-tools/file-manager/
    """

    def test_file_manager(self):
        from griptape.tools import FileManager

        client = FileManager()

        assert client is not None
