from griptape.common import Reference
from griptape.loaders.text_loader import TextLoader


class TestBaseLoader:
    def test_parse(self):
        loader = TextLoader(reference=Reference(authors=["jason"], title="pies"))

        artifact = loader.parse(b"hello")

        assert artifact.value == "hello"
        assert artifact.encoding == "utf-8"
        assert artifact.meta == {}
        assert artifact.reference == loader.reference
