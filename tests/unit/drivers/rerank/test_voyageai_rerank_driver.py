from unittest.mock import Mock

import pytest

from griptape.artifacts import TextArtifact
from griptape.drivers.rerank.voyageai import VoyageAiRerankDriver


class TestVoyageAiRerankDriver:
    # ---------------------------------------------------------------------------
    # Fixtures
    # ---------------------------------------------------------------------------

    @pytest.fixture()
    def mock_client(self, mocker):
        mock_client = mocker.patch("voyageai.Client").return_value
        mock_client.rerank.return_value = Mock(
            results=[
                Mock(index=1, document="bar", relevance_score=1.0),
                Mock(index=0, document="foo", relevance_score=0.5),
            ]
        )

        return mock_client

    @pytest.fixture()
    def mock_empty_client(self, mocker):
        mock_client = mocker.patch("voyageai.Client").return_value
        mock_client.rerank.side_effect = Exception("Client should not be called")

        return mock_client

    # ---------------------------------------------------------------------------
    # Defaults / instantiation
    # ---------------------------------------------------------------------------

    def test_init(self):
        assert VoyageAiRerankDriver()

    def test_default_model(self):
        assert VoyageAiRerankDriver().model == "rerank-2.5"

    def test_default_api_key_is_none(self):
        assert VoyageAiRerankDriver().api_key is None

    def test_default_top_k_is_none(self):
        assert VoyageAiRerankDriver().top_k is None

    def test_client_is_constructed_with_api_key(self, mocker):
        mock_client_cls = mocker.patch("voyageai.Client")

        driver = VoyageAiRerankDriver(api_key="my-secret-key")
        _ = driver.client

        mock_client_cls.assert_called_once_with(api_key="my-secret-key")

    def test_client_override(self, mocker):
        mock_client_cls = mocker.patch("voyageai.Client")
        custom_client = mocker.MagicMock()

        driver = VoyageAiRerankDriver(client=custom_client)

        assert driver.client is custom_client
        mock_client_cls.assert_not_called()

    # ---------------------------------------------------------------------------
    # run() — empty / falsy inputs
    # ---------------------------------------------------------------------------

    def test_run_empty_artifacts_returns_empty(self, mock_empty_client):
        driver = VoyageAiRerankDriver(api_key="api-key")

        result = driver.run("hello", artifacts=[])

        assert result == []
        mock_empty_client.rerank.assert_not_called()

    def test_run_all_falsy_artifacts_returns_empty(self, mock_empty_client):
        driver = VoyageAiRerankDriver(api_key="api-key")

        result = driver.run("hello", artifacts=[TextArtifact(""), TextArtifact("  ")])

        assert result == []
        mock_empty_client.rerank.assert_not_called()

    def test_run_with_mixed_falsy_and_truthy_artifacts(self, mocker):
        mock_client = mocker.patch("voyageai.Client").return_value
        # "first" and "third" survive filtering and are sent to the API at index 0 and 1 respectively.
        mock_client.rerank.return_value = Mock(
            results=[
                Mock(index=1, document="third", relevance_score=0.95),
                Mock(index=0, document="first", relevance_score=0.60),
            ]
        )

        artifacts = [TextArtifact("first"), TextArtifact("   "), TextArtifact("third")]
        driver = VoyageAiRerankDriver(api_key="api-key")

        result = driver.run("query", artifacts=artifacts)

        mock_client.rerank.assert_called_once_with(
            query="query", documents=["first", "third"], model="rerank-2.5", top_k=None
        )
        assert len(result) == 2
        assert result[0].value == "third"
        assert result[1].value == "first"

    # ---------------------------------------------------------------------------
    # run() — happy path
    # ---------------------------------------------------------------------------

    def test_run_returns_artifacts_in_relevance_order(self, mock_client):
        driver = VoyageAiRerankDriver(api_key="api-key")

        result = driver.run("hello", artifacts=[TextArtifact("foo"), TextArtifact("bar")])

        assert len(result) == 2
        assert result[0].value == "bar"
        assert result[1].value == "foo"

    def test_run_single_artifact(self, mocker):
        mock_client = mocker.patch("voyageai.Client").return_value
        mock_client.rerank.return_value = Mock(results=[Mock(index=0, document="only one", relevance_score=0.99)])

        driver = VoyageAiRerankDriver(api_key="api-key")
        result = driver.run("query", artifacts=[TextArtifact("only one")])

        assert len(result) == 1
        assert result[0].value == "only one"

    def test_run_empty_results_returns_empty(self, mocker):
        mock_client = mocker.patch("voyageai.Client").return_value
        mock_client.rerank.return_value = Mock(results=[])

        driver = VoyageAiRerankDriver(api_key="api-key")
        result = driver.run("query", artifacts=[TextArtifact("only one")])

        assert result == []

    # ---------------------------------------------------------------------------
    # run() — request parameters
    # ---------------------------------------------------------------------------

    def test_run_passes_model_and_top_k(self, mock_client):
        driver = VoyageAiRerankDriver(api_key="api-key", model="rerank-2.5-lite", top_k=1)

        driver.run("hello", artifacts=[TextArtifact("foo"), TextArtifact("bar")])

        mock_client.rerank.assert_called_once_with(
            query="hello", documents=["foo", "bar"], model="rerank-2.5-lite", top_k=1
        )

    def test_run_passes_top_k_none_when_unset(self, mock_client):
        driver = VoyageAiRerankDriver(api_key="api-key")

        driver.run("hello", artifacts=[TextArtifact("foo"), TextArtifact("bar")])

        mock_client.rerank.assert_called_once_with(
            query="hello", documents=["foo", "bar"], model="rerank-2.5", top_k=None
        )
