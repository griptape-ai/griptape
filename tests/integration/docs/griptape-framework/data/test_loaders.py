from sqlalchemy.exc import ArgumentError
import pytest


class TestLoaders:
    """
    https://docs.griptape.ai/en/latest/griptape-framework/data/loaders/
    """
    def test_pdf_loader(self):
        from griptape.loaders import PdfLoader

        with pytest.raises(FileNotFoundError):
            PdfLoader().load("path/to/file.pdf")

        with pytest.raises(FileNotFoundError):
            PdfLoader().load_collection(["path/to/file_1.pdf", "path/to/file_2.pdf"])

    def test_sql_loader(self):
        from griptape.loaders import SqlLoader
        from griptape.drivers import SqlDriver

        with pytest.raises(ArgumentError):
            SqlLoader(
                sql_driver=SqlDriver(engine_url="..."),
            ).load("SELECT * FROM users;")

        with pytest.raises(ArgumentError):
            SqlLoader(
                sql_driver=SqlDriver(engine_url="..."),
            ).load_collection(["SELECT * FROM users;", "SELECT * FROM products;"])

    def test_text_loader(self):
        from pathlib import Path
        from griptape.loaders import TextLoader

        result = TextLoader().load("my text")

        assert result[0] is not None
        assert result[0].value == "my text"

        with pytest.raises(FileNotFoundError):
            TextLoader().load(Path("path/to/file.txt"))

        with pytest.raises(FileNotFoundError):
            TextLoader().load_collection(
                ["my text", "my other text", Path("path/to/file.txt")]
            )

    def test_web_loader(self):
        from griptape.loaders import WebLoader

        result = WebLoader().load("https://www.griptape.ai")

        assert result[0] is not None
        assert result[0].value is not None

        result = WebLoader().load_collection(
            ["https://www.griptape.ai", "https://docs.griptape.ai"]
        )

        for value in result.values():
            assert value[0] is not None
