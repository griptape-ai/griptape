from unittest.mock import MagicMock

import pytest

from griptape.drivers.vector.redis import RedisVectorStoreDriver
from tests.mocks.mock_embedding_driver import MockEmbeddingDriver


class TestRedisVectorStorageDriver:
    @pytest.fixture(autouse=True)
    def mock_client(self, mocker):
        return mocker.patch("redis.Redis").return_value

    @pytest.fixture()
    def mock_keys(self, mock_client):
        mock_client.keys.return_value = [b"some_vector_id"]
        return mock_client.keys

    @pytest.fixture()
    def mock_hgetall(self, mock_client):
        mock_client.hgetall.return_value = {
            b"vector": b"\x00\x00\x80?\x00\x00\x00@\x00\x00@@",
            b"metadata": b'{"foo": "bar"}',
        }
        return mock_client.hgetall

    @pytest.fixture()
    def driver(self):
        return RedisVectorStoreDriver(
            host="localhost", port=6379, index="test_index", db=0, embedding_driver=MockEmbeddingDriver()
        )

    @pytest.fixture()
    def mock_search(self, mock_client):
        mock_client.ft.return_value.search.return_value.docs = [
            MagicMock(
                id="some_namespace:some_vector_id",
                score="0.456198036671",
                metadata='{"foo": "bar"}',
                vec_string="[1.0, 2.0, 3.0]",
            )
        ]
        return mock_client.ft.return_value.search

    def test_upsert_vector(self, driver):
        assert (
            driver.upsert_vector([1.0, 2.0, 3.0], vector_id="some_vector_id", namespace="some_namespace")
            == "some_vector_id"
        )

    def test_load_entry(self, driver, mock_hgetall):
        entry = driver.load_entry("some_vector_id")
        mock_hgetall.assert_called_once_with("some_vector_id")
        assert entry.id == "some_vector_id"
        assert entry.vector == [1.0, 2.0, 3.0]
        assert entry.meta == {"foo": "bar"}

    def test_load_entry_with_namespace(self, driver, mock_hgetall):
        entry = driver.load_entry("some_vector_id", namespace="some_namespace")
        mock_hgetall.assert_called_once_with("some_namespace:some_vector_id")
        assert entry.id == "some_vector_id"
        assert entry.vector == [1.0, 2.0, 3.0]
        assert entry.meta == {"foo": "bar"}

    def test_load_entries(self, driver, mock_keys, mock_hgetall):
        entries = driver.load_entries()
        mock_keys.assert_called_once_with("*")
        mock_hgetall.assert_called_once_with("some_vector_id")
        assert len(entries) == 1
        assert entries[0].vector == [1.0, 2.0, 3.0]
        assert entries[0].meta == {"foo": "bar"}

    def test_load_entries_with_namespace(self, driver, mock_keys, mock_hgetall):
        entries = driver.load_entries(namespace="some_namespace")
        mock_keys.assert_called_once_with("some_namespace:*")
        mock_hgetall.assert_called_once_with("some_namespace:some_vector_id")
        assert len(entries) == 1
        assert entries[0].vector == [1.0, 2.0, 3.0]
        assert entries[0].meta == {"foo": "bar"}

    def test_query_vector(self, driver, mock_search):
        results = driver.query_vector([0.0, 0.5])
        mock_search.assert_called_once()
        assert len(results) == 1
        assert results[0].namespace == "some_namespace"
        assert results[0].id == "some_vector_id"
        assert results[0].score == 0.456198036671
        assert results[0].meta == {"foo": "bar"}
        assert results[0].vector is None

    def test_query_vector_with_include_vectors(self, driver, mock_search):
        results = driver.query_vector([0.0, 0.5], include_vectors=True)
        mock_search.assert_called_once()
        assert len(results) == 1
        assert results[0].namespace == "some_namespace"
        assert results[0].id == "some_vector_id"
        assert results[0].score == 0.456198036671
        assert results[0].meta == {"foo": "bar"}
        assert results[0].vector == [1.0, 2.0, 3.0]

    def test_query(self, driver, mock_search):
        results = driver.query("Some query")
        mock_search.assert_called_once()
        assert len(results) == 1
        assert results[0].namespace == "some_namespace"
        assert results[0].id == "some_vector_id"
        assert results[0].score == 0.456198036671
        assert results[0].meta == {"foo": "bar"}
        assert results[0].vector is None

    def test_query_with_include_vectors(self, driver, mock_search):
        results = driver.query("Some query", include_vectors=True)
        mock_search.assert_called_once()
        assert len(results) == 1
        assert results[0].namespace == "some_namespace"
        assert results[0].id == "some_vector_id"
        assert results[0].score == 0.456198036671
        assert results[0].meta == {"foo": "bar"}
        assert results[0].vector == [1.0, 2.0, 3.0]

    @pytest.mark.parametrize(
        "namespace",
        ["some_namespace", "tenant-a", "a.b.c", "9f3c-4d1e-88ab", "user 12", "ns:sub"],
    )
    def test_query_vector_leaves_ordinary_namespaces_intact(self, driver, mock_search, namespace):
        driver.query_vector([0.0, 0.5], namespace=namespace)

        assert mock_search.call_args[0][0].query_string().startswith(f"(@namespace:{{{namespace}}})")

    @pytest.mark.parametrize(
        ("namespace", "expected"),
        [
            ("tenant-a|tenant-b", "(@namespace:{tenant-a\\|tenant-b})"),
            ("x} | (@namespace:{y}", "(@namespace:{x\\} \\| (@namespace:\\{y\\}})"),
            ("a\\|b", "(@namespace:{a\\\\\\|b})"),
        ],
    )
    def test_query_vector_escapes_namespace_tag_metacharacters(self, driver, mock_search, namespace, expected):
        driver.query_vector([0.0, 0.5], namespace=namespace)

        assert mock_search.call_args[0][0].query_string().startswith(expected)

    @pytest.mark.parametrize(
        ("namespace", "expected"),
        [
            ("some_namespace", "some_namespace:*"),
            ("tenant-a", "tenant-a:*"),
            ("tenant*", "tenant\\*:*"),
            ("tenant[ab]", "tenant\\[ab\\]:*"),
            ("tenant?", "tenant\\?:*"),
        ],
    )
    def test_load_entries_escapes_namespace_glob_metacharacters(
        self, driver, mock_keys, mock_hgetall, namespace, expected
    ):
        driver.load_entries(namespace=namespace)

        mock_keys.assert_called_once_with(expected)
