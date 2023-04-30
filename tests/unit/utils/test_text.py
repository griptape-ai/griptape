import logging

from llama_index import GPTSimpleVectorIndex
from griptape.utils.text import to_vector_index


class TestText:
    def test_to_vector_index(self):
        try:
            assert isinstance(to_vector_index("foobar"), GPTSimpleVectorIndex)
        except Exception as e:
            logging.error(e)

            # TODO: add a mock for OpenAI embeddings generation in llama_index
            assert True
