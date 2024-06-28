from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import MetadataGenerationRagModule


class TestMetadataGenerationModule:
    def test_run(self):
        module = MetadataGenerationRagModule()

        assert "foo" in module.run(
            RagContext(
                module_params={"MetadataGenerationRagModule": {"metadata": "foo"}},
                query="test"
            )
        ).before_query[0]

    def test_run_with_override(self):
        module = MetadataGenerationRagModule(metadata="bar")

        assert "bar" in module.run(
            RagContext(
                module_params={"MetadataGenerationRagModule": {"query_params": {"metadata": "foo"}}},
                query="test"
            )
        ).before_query[0]
