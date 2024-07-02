from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import MetadataBeforeResponseRagModule


class TestMetadataBeforeResponseRagModule:
    def test_run(self):
        module = MetadataBeforeResponseRagModule(name="foo")

        assert "foo" in module.run(
            RagContext(
                module_params={"foo": {"metadata": "foo"}},
                query="test"
            )
        ).before_query[0]

    def test_run_with_override(self):
        module = MetadataBeforeResponseRagModule(name="foo", metadata="bar")

        assert "bar" in module.run(
            RagContext(
                module_params={"foo": {"query_params": {"metadata": "foo"}}},
                query="test"
            )
        ).before_query[0]
