from griptape.loaders import TextLoader
from griptape import utils
from concurrent import futures
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver

MAX_TOKENS = 50


class TestFileUtils:
    def test_load_file(self):
        file = utils.load_file("tests/resources/foobar-many.txt")

        assert file.decode("utf-8").startswith("foobar foobar foobar")
        assert len(file.decode("utf-8")) == 4563

    def test_load_files(self):
        sources = ["tests/resources/foobar-many.txt", "tests/resources/foobar-many.txt", "tests/resources/small.png"]
        files = utils.load_files(sources, futures_executor=futures.ThreadPoolExecutor(max_workers=1))
        assert len(files) == 2

        test_file = files[utils.str_to_hash("tests/resources/foobar-many.txt")]
        assert len(test_file) == 4563
        assert test_file.decode("utf-8").startswith("foobar foobar foobar")

        small_file = files[utils.str_to_hash("tests/resources/small.png")]
        assert len(small_file) == 97
        assert small_file[:8] == b"\x89PNG\r\n\x1a\n"

    def test_load_file_with_loader(self):
        file = utils.load_file("tests/resources/foobar-many.txt")
        artifacts = TextLoader(max_tokens=MAX_TOKENS, embedding_driver=MockEmbeddingDriver()).load(file)

        assert len(artifacts) == 39
        assert isinstance(artifacts, list)
        assert artifacts[0].value.startswith("foobar foobar foobar")

    def test_load_files_with_loader(self):
        sources = ["tests/resources/foobar-many.txt"]
        files = utils.load_files(sources)
        loader = TextLoader(max_tokens=MAX_TOKENS, embedding_driver=MockEmbeddingDriver())
        collection = loader.load_collection(list(files.values()))

        test_file_artifacts = collection[loader.to_key(files[utils.str_to_hash("tests/resources/foobar-many.txt")])]
        assert len(test_file_artifacts) == 39
        assert isinstance(test_file_artifacts, list)
        assert test_file_artifacts[0].value.startswith("foobar foobar foobar")
