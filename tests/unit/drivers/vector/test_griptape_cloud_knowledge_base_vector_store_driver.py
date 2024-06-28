import uuid
from unittest.mock import Mock, patch
from griptape.drivers import GriptapeCloudKnowledgeBaseVectorStoreDriver


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


test_ids = [str(uuid.uuid4()), str(uuid.uuid4())]
test_vecs = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
test_namespaces = [str(uuid.uuid4()), str(uuid.uuid4())]
test_metas = [{"key": "value1"}, {"key": "value2"}]
test_scores = [0.7, 0.8]
test_entries = {
    "entries": [
        {
            "id": test_ids[0],
            "vector": test_vecs[0],
            "namespace": test_namespaces[0],
            "meta": test_metas[0],
            "score": test_scores[0],
        },
        {
            "id": test_ids[1],
            "vector": test_vecs[1],
            "namespace": test_namespaces[1],
            "meta": test_metas[1],
            "score": test_scores[1],
        },
    ]
}


class TestGriptapeCloudKnowledgeBaseVectorStoreDriver:
    def mock_requests_post(*args, **kwargs):
        return MockResponse(test_entries, 200)

    @patch("requests.post", side_effect=mock_requests_post)
    def test_query(self, mock_post):
        driver = GriptapeCloudKnowledgeBaseVectorStoreDriver(api_key="foo", knowledge_base_id="bar")

        result = driver.query(
            "some query", count=10, namespace="foo", include_vectors=True, distance_metric="bar", filter={"foo": "bar"}
        )

        assert result[0].id == test_ids[0]
        assert result[1].id == test_ids[1]
        assert result[0].vector == test_vecs[0]
        assert result[1].vector == test_vecs[1]
        assert result[0].namespace == test_namespaces[0]
        assert result[1].namespace == test_namespaces[1]
        assert result[0].meta == test_metas[0]
        assert result[1].meta == test_metas[1]
        assert result[0].score == test_scores[0]
        assert result[1].score == test_scores[1]

    @patch("requests.post", side_effect=mock_requests_post)
    def test_query_defaults(self, mock_post):
        driver = GriptapeCloudKnowledgeBaseVectorStoreDriver(api_key="foo", knowledge_base_id="bar")

        result = driver.query("some query")

        assert result[0].id == test_ids[0]
        assert result[1].id == test_ids[1]
        assert result[0].vector == test_vecs[0]
        assert result[1].vector == test_vecs[1]
        assert result[0].namespace == test_namespaces[0]
        assert result[1].namespace == test_namespaces[1]
        assert result[0].meta == test_metas[0]
        assert result[1].meta == test_metas[1]
        assert result[0].score == test_scores[0]
        assert result[1].score == test_scores[1]
