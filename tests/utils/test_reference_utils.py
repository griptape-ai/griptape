from griptape.artifacts import TextArtifact
from griptape.common import Reference
from griptape.engines.rag.modules import PromptResponseRagModule
from tests.mocks.mock_prompt_driver import MockPromptDriver


class TestReferenceUtils:
    def test_references_from_artifacts(self):
        module = PromptResponseRagModule(prompt_driver=MockPromptDriver())
        reference1 = Reference(title="foo")
        reference2 = Reference(title="bar")
        artifacts = [
            TextArtifact("foo", reference=reference1),
            TextArtifact("foo", reference=reference1),
            TextArtifact("foo"),
            TextArtifact("foo", reference=reference2),
        ]
        references = module.references_from_artifacts(artifacts)

        assert len(references) == 2
        assert references[0].id == reference1.id
        assert references[1].id == reference2.id
