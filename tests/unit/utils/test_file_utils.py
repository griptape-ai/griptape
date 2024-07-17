import os
from concurrent import futures

from griptape import utils
from griptape.loaders import TextLoader
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver

MAX_TOKENS = 50


class TestFileUtils:
    def test_load_file(self):
        dirname = os.path.dirname(__file__)
        file = utils.load_file(os.path.join(dirname, "../../resources/foobar-many.txt"))

        assert file.decode("utf-8").startswith("foobar foobar foobar")

    def test_load_files(self):
        dirname = os.path.dirname(__file__)
        sources = ["resources/foobar-many.txt", "resources/foobar-many.txt", "resources/small.png"]
        sources = [os.path.join(dirname, "../../", source) for source in sources]
        files = utils.load_files(sources, futures_executor=futures.ThreadPoolExecutor(max_workers=1))
        assert len(files) == 2

        test_file = files[utils.str_to_hash(sources[0])]
        assert test_file.decode("utf-8").startswith("foobar foobar foobar")

        small_file = files[utils.str_to_hash(sources[2])]
        assert len(small_file) == 97
        assert small_file[:8] == b"\x89PNG\r\n\x1a\n"

    def test_load_file_with_loader(self):
        dirname = os.path.dirname(__file__)
        file = utils.load_file(os.path.join(dirname, "../../", "resources/foobar-many.txt"))
        artifacts = TextLoader(max_tokens=MAX_TOKENS, embedding_driver=MockEmbeddingDriver()).load(file)

        assert len(artifacts) == 39
        assert isinstance(artifacts, list)
        assert artifacts[0].value.startswith("foobar foobar foobar")

    def test_load_files_with_loader(self):
        dirname = os.path.dirname(__file__)
        sources = ["resources/foobar-many.txt"]
        sources = [os.path.join(dirname, "../../", source) for source in sources]
        files = utils.load_files(sources)
        loader = TextLoader(max_tokens=MAX_TOKENS, embedding_driver=MockEmbeddingDriver())
        collection = loader.load_collection(list(files.values()))

        test_file_artifacts = collection[loader.to_key(files[utils.str_to_hash(sources[0])])]
        assert len(test_file_artifacts) == 39
        assert isinstance(test_file_artifacts, list)
        assert test_file_artifacts[0].value.startswith("foobar foobar foobar")
