from griptape.artifacts import TextArtifact
from griptape.drivers import BaseVectorStoreDriver


class TestQueryResult:
    def test_to_artifact(self):
        query_result = BaseVectorStoreDriver.QueryResult(
            id="test",
            vector=None,
            score=0,
            meta={
                "artifact": TextArtifact("foo").to_json()
            }
        )
        assert query_result.to_artifact().value == "foo"
