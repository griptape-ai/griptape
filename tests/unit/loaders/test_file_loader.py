import os
from pathlib import Path
import pytest
from griptape import utils
from griptape.loaders.file_loader import FileLoader


class TestFileLoader:
    @pytest.fixture
    def loader(self):
        return FileLoader(dir_name="../../resources")

    def test_load_with_path(self, loader):
        path = Path(os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "../../resources/test.txt"
        ))

        artifacts = loader.load(path)

        assert len(artifacts) == 1
        assert artifacts[0].name == "test.txt"
        assert artifacts[0].dir == "../../resources"
        assert artifacts[0].value.decode().startswith("foobar foobar foobar")
        assert artifacts[0].full_path in str(path)

    def test_load_collection_with_path(self, loader):
        text_path = Path(os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "../../resources/test.txt"
        ))
        pdf_path = Path(os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "../../resources/bitcoin.pdf"
        ))
        artifacts = loader.load_collection([text_path, pdf_path])

        text_key = utils.str_to_hash(str(text_path))
        assert list(artifacts.keys())[0] == text_key
        assert len(artifacts[text_key]) == 1
        assert artifacts[text_key][0].name == "test.txt"
        assert artifacts[text_key][0].dir == "../../resources"
        assert artifacts[text_key][0].full_path in str(text_path) 
        
        pdf_key = utils.str_to_hash(str(pdf_path))
        assert list(artifacts.keys())[1] == pdf_key
        assert len(artifacts[pdf_key]) == 1
        assert artifacts[pdf_key][0].name == "bitcoin.pdf"
        assert artifacts[pdf_key][0].dir == "../../resources"
        assert artifacts[pdf_key][0].full_path in str(pdf_path) 
