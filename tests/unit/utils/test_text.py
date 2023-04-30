from llama_index import GPTSimpleVectorIndex
from griptape.utils.text import to_vector_index


class TestText():
    def test_to_vector_index(self):
        assert isinstance(to_vector_index("foobar"), GPTSimpleVectorIndex)
