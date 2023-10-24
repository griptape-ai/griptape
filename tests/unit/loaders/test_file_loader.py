import os
from pathlib import Path
import pytest
from griptape import utils
from griptape.artifacts import TextArtifact, BlobArtifact
from griptape.loaders.file_loader import FileLoader


class TestFileLoader:
    @pytest.fixture
    def loader(self):
        return FileLoader()

    def test_load_with_path(self, loader):
        path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "../../resources/test.txt",
        )

        artifact = loader.load(path)

        assert isinstance(artifact, BlobArtifact)
        assert artifact.name == "test.txt"
        assert artifact.dir_name.endswith("../../resources")
        assert artifact.value.decode().startswith("foobar foobar foobar")
        assert artifact.full_path in str(path)

    def test_load_with_encoding(self):
        loader = FileLoader(encoding="utf-8")
        path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "../../resources/test.txt",
        )

        artifact = loader.load(path)

        assert isinstance(artifact, TextArtifact)
        assert artifact.name == "test.txt"
        assert artifact.value.startswith("foobar foobar foobar")

    def test_load_collection_with_path(self, loader):
        text_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "../../resources/test.txt",
        )
        pdf_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "../../resources/bitcoin.pdf",
        )
        artifacts = loader.load_collection([text_path, pdf_path])

        text_key = utils.str_to_hash(str(text_path))
        assert list(artifacts.keys())[0] == text_key
        assert artifacts[text_key].name == "test.txt"
        assert artifacts[text_key].dir_name.endswith("../../resources")
        assert artifacts[text_key].full_path in str(text_path)

        pdf_key = utils.str_to_hash(str(pdf_path))
        assert list(artifacts.keys())[1] == pdf_key
        assert artifacts[pdf_key].name == "bitcoin.pdf"
        assert artifacts[pdf_key].dir_name.endswith("../../resources")
        assert artifacts[pdf_key].full_path in str(pdf_path)
