from typing import TYPE_CHECKING

import boto3
import pytest
from botocore.stub import Stubber

from griptape.artifacts import TextArtifact
from griptape.drivers.rerank.amazon_bedrock_rerank_driver import AmazonBedrockRerankDriver

if TYPE_CHECKING:
    from mypy_boto3_bedrock_agent_runtime.type_defs import RerankResultTypeDef


class TestAmazonBedrockRerankDriver:
    # ---------------------------------------------------------------------------
    # Fixtures
    # ---------------------------------------------------------------------------

    @pytest.fixture()
    def session(self):
        return boto3.Session(region_name="us-east-1")

    @pytest.fixture()
    def driver(self, session):
        """Driver wired to a real boto3 session; individual tests inject a Stubber."""
        return AmazonBedrockRerankDriver(session=session)

    @pytest.fixture()
    def driver_with_top_n(self, session):
        return AmazonBedrockRerankDriver(session=session, top_n=2)

    # ---------------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------------

    def _make_rerank_response(self, results: list[dict]) -> dict:
        """Build a minimal Bedrock rerank API response dict."""
        return {
            "results": results,
            "ResponseMetadata": {
                "RequestId": "test-request-id",
                "HTTPStatusCode": 200,
                "HTTPHeaders": {},
                "RetryAttempts": 0,
            },
        }

    def _make_expected_rerank_params(
        self,
        model_arn: str,
        query: str,
        texts: list[str],
        *,
        top_n: int | None = None,
        next_token: str | None = None,
    ) -> dict:
        bedrock_reranking_configuration: dict = {"modelConfiguration": {"modelArn": model_arn}}

        if top_n is not None:
            bedrock_reranking_configuration["numberOfResults"] = top_n

        expected_params = {
            "queries": [{"type": "TEXT", "textQuery": {"text": query}}],
            "sources": [
                {
                    "type": "INLINE",
                    "inlineDocumentSource": {"type": "TEXT", "textDocument": {"text": text}},
                }
                for text in texts
            ],
            "rerankingConfiguration": {
                "type": "BEDROCK_RERANKING_MODEL",
                "bedrockRerankingConfiguration": bedrock_reranking_configuration,
            },
        }

        if next_token is not None:
            expected_params["nextToken"] = next_token

        return expected_params

    # ---------------------------------------------------------------------------
    # Defaults / instantiation
    # ---------------------------------------------------------------------------

    def test_default_model(self, driver):
        assert driver.model == "cohere.rerank-v3-5:0"

    def test_default_top_n_is_none(self, driver):
        assert driver.top_n is None

    def test_model_arn_contains_region_and_model(self, driver):
        arn = driver.model_arn
        assert "us-east-1" in arn
        assert driver.model in arn
        assert arn.startswith("arn:aws:bedrock:")

    def test_model_arn_custom_model(self, session):
        driver = AmazonBedrockRerankDriver(session=session, model="amazon.rerank-v1:0")
        assert "amazon.rerank-v1:0" in driver.model_arn

    def test_model_arn_uses_client_metadata(self, mocker, session):
        mock_client = mocker.MagicMock()
        mock_client.meta.partition = "aws-us-gov"
        mock_client.meta.region_name = "us-gov-west-1"

        driver = AmazonBedrockRerankDriver(session=session, client=mock_client)

        assert driver.model_arn == "arn:aws-us-gov:bedrock:us-gov-west-1::foundation-model/cohere.rerank-v3-5:0"

    # ---------------------------------------------------------------------------
    # run() — empty / falsy inputs
    # ---------------------------------------------------------------------------

    def test_run_empty_artifacts_returns_empty(self, mocker, session):
        """When artifacts list is empty, client must never be called."""
        mock_client = mocker.MagicMock()
        driver = AmazonBedrockRerankDriver(session=session, client=mock_client)

        result = driver.run("query", artifacts=[])

        assert result == []
        mock_client.rerank.assert_not_called()

    def test_run_all_falsy_artifacts_returns_empty(self, mocker, session):
        """When all artifacts are falsy, client must never be called."""
        mock_client = mocker.MagicMock()
        driver = AmazonBedrockRerankDriver(session=session, client=mock_client)

        result = driver.run("query", artifacts=[TextArtifact("   "), TextArtifact("")])

        assert result == []
        mock_client.rerank.assert_not_called()

    def test_run_with_empty_and_falsy_artifacts(self, session):
        """Falsy artifacts should be filtered out, and the returned indices mapped correctly."""
        client = session.client("bedrock-agent-runtime")
        stubber = Stubber(client)

        artifacts = [TextArtifact("first"), TextArtifact("   "), TextArtifact("third")]

        # AWS returns index-1 (which maps to "third") first, then index-0 (which maps to "first")
        rerank_response = self._make_rerank_response(
            [
                {"index": 1, "relevanceScore": 0.95},
                {"index": 0, "relevanceScore": 0.60},
            ]
        )

        driver = AmazonBedrockRerankDriver(session=session, client=client)
        stubber.add_response(
            "rerank", rerank_response, self._make_expected_rerank_params(driver.model_arn, "query", ["first", "third"])
        )
        stubber.activate()

        result = driver.run("query", artifacts=artifacts)

        assert len(result) == 2
        assert result[0].value == "third"
        assert result[1].value == "first"

    # ---------------------------------------------------------------------------
    # run() — happy path via botocore Stubber
    # ---------------------------------------------------------------------------

    def test_run_returns_artifacts_in_relevance_order(self, session):
        """Results are mapped back through the original artifacts list by index."""
        client = session.client("bedrock-agent-runtime")
        stubber = Stubber(client)

        artifacts = [TextArtifact("first"), TextArtifact("second"), TextArtifact("third")]

        # AWS returns index-2 first (highest score), then index-0
        rerank_response = self._make_rerank_response(
            [
                {"index": 2, "relevanceScore": 0.95},
                {"index": 0, "relevanceScore": 0.60},
                {"index": 1, "relevanceScore": 0.10},
            ]
        )

        driver = AmazonBedrockRerankDriver(session=session, client=client)
        stubber.add_response(
            "rerank",
            rerank_response,
            self._make_expected_rerank_params(driver.model_arn, "what is griptape?", ["first", "second", "third"]),
        )
        stubber.activate()

        result = driver.run("what is griptape?", artifacts=artifacts)

        assert len(result) == 3
        # _post_process maps results[i]["index"] back to original artifacts
        assert result[0].value == "third"  # index 2
        assert result[1].value == "first"  # index 0
        assert result[2].value == "second"  # index 1

    def test_run_with_top_n(self, session):
        """When top_n is set, numberOfResults should be included in the request."""
        client = session.client("bedrock-agent-runtime")
        stubber = Stubber(client)

        artifacts = [TextArtifact("alpha"), TextArtifact("beta")]

        rerank_response = self._make_rerank_response(
            [
                {"index": 1, "relevanceScore": 0.80},
                {"index": 0, "relevanceScore": 0.40},
            ]
        )

        driver = AmazonBedrockRerankDriver(session=session, client=client, top_n=2)
        stubber.add_response(
            "rerank",
            rerank_response,
            self._make_expected_rerank_params(driver.model_arn, "query", ["alpha", "beta"], top_n=2),
        )
        stubber.activate()

        result = driver.run("query", artifacts=artifacts)

        assert len(result) == 2
        assert result[0].value == "beta"  # index 1 wins
        assert result[1].value == "alpha"  # index 0

    def test_run_single_artifact(self, session):
        client = session.client("bedrock-agent-runtime")
        stubber = Stubber(client)

        artifacts = [TextArtifact("only one")]
        rerank_response = self._make_rerank_response([{"index": 0, "relevanceScore": 0.99}])

        driver = AmazonBedrockRerankDriver(session=session, client=client)
        stubber.add_response(
            "rerank", rerank_response, self._make_expected_rerank_params(driver.model_arn, "query", ["only one"])
        )
        stubber.activate()

        result = driver.run("query", artifacts=artifacts)

        assert len(result) == 1
        assert result[0].value == "only one"

    # ---------------------------------------------------------------------------
    # _post_process — unit tests (pure function, no AWS calls needed)
    # ---------------------------------------------------------------------------

    def test_post_process_reorders_by_response_index(self):
        artifacts = [TextArtifact("A"), TextArtifact("B"), TextArtifact("C")]
        response: list[RerankResultTypeDef] = [
            {"index": 2, "relevanceScore": 0.9},
            {"index": 0, "relevanceScore": 0.5},
        ]
        result = AmazonBedrockRerankDriver._post_process(response, artifacts)
        assert result[0].value == "C"
        assert result[1].value == "A"

    def test_post_process_empty_response(self):
        artifacts = [TextArtifact("A"), TextArtifact("B")]
        result = AmazonBedrockRerankDriver._post_process([], artifacts)
        assert result == []

    # ---------------------------------------------------------------------------
    # Pagination — nextToken handling
    # ---------------------------------------------------------------------------

    def test_run_handles_pagination(self, mocker, session):
        """When a nextToken is present, the driver should fetch all pages."""
        page1 = {
            "results": [{"index": 0, "relevanceScore": 0.9}],
            "nextToken": "page2token",
            "ResponseMetadata": {"RequestId": "r1", "HTTPStatusCode": 200, "HTTPHeaders": {}, "RetryAttempts": 0},
        }
        page2 = self._make_rerank_response([{"index": 1, "relevanceScore": 0.5}])

        mock_client = mocker.MagicMock()
        mock_client.meta.partition = "aws"
        mock_client.meta.region_name = "us-east-1"
        mock_client.rerank.side_effect = [page1, page2]

        artifacts = [TextArtifact("first"), TextArtifact("second")]
        driver = AmazonBedrockRerankDriver(session=session, client=mock_client)
        result = driver.run("query", artifacts=artifacts)

        assert mock_client.rerank.call_count == 2
        mock_client.rerank.assert_has_calls(
            [
                mocker.call(**self._make_expected_rerank_params(driver.model_arn, "query", ["first", "second"])),
                mocker.call(
                    **self._make_expected_rerank_params(
                        driver.model_arn, "query", ["first", "second"], next_token="page2token"
                    )
                ),
            ]
        )
        assert len(result) == 2
        assert result[0].value == "first"
        assert result[1].value == "second"
