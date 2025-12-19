from abc import ABC, abstractmethod
from unittest.mock import patch

import pytest

from griptape.artifacts import TextArtifact
from griptape.drivers.vector import BaseVectorStoreDriver


class TestBaseVectorStoreDriver(ABC):
    @pytest.fixture()
    @abstractmethod
    def driver(self, *args, **kwargs) -> BaseVectorStoreDriver: ...

    def test_insert(self, driver, mocker):
        spy = mocker.patch.object(driver, "insert_vector", return_value="vid123")
        returned_id = driver.insert(
            "foobar",
            namespace="ns1",
            meta={"k": "v"},
            vector_id="vid123",
        )
        # Assert
        assert returned_id == "vid123"
        assert spy.call_count == 1
        args, kwargs = spy.call_args
        # vector should come from embedding driver mock: [0, 1]
        assert args[0] == [0, 1]
        assert kwargs["namespace"] == "ns1"
        assert kwargs["vector_id"] == "vid123"
        # meta should be merged and include serialized artifact
        assert kwargs["meta"]["k"] == "v"
        assert "artifact" in kwargs["meta"]

    def test_insert_generates_vector_id_when_not_provided(self, driver, mocker):
        spy = mocker.patch.object(driver, "insert_vector", return_value="auto-id")

        result_id = driver.insert(TextArtifact("hello"), namespace="ns2")

        assert result_id == "auto-id"
        assert spy.call_count == 1
        _, kwargs = spy.call_args
        # Should auto-generate some vector_id string
        assert isinstance(kwargs["vector_id"], str)
        assert len(kwargs["vector_id"]) > 0
        assert kwargs["namespace"] == "ns2"
        assert "artifact" in kwargs["meta"]

    def test_insert_collection_list(self, driver, mocker):
        # Prepare two deterministic return ids but allow any execution order
        ids = ["a1", "a2"]
        mock = mocker.patch.object(driver, "insert_vector", side_effect=ids)

        result = driver.insert_collection([TextArtifact("one"), TextArtifact("two")])

        # Order of execution may vary across Python/platforms, so compare as sets
        assert len(result) == 2
        assert set(result) == set(ids)
        # insert is called under the hood once per artifact
        assert mock.call_count == 2
        # ensure namespace is None for list inputs
        for call in mock.call_args_list:
            assert call.kwargs.get("namespace") is None
            assert "artifact" in call.kwargs.get("meta", {})

    def test_insert_collection_dict(self, driver, mocker):
        # Generate IDs deterministically per-namespace regardless of interleaving
        prefix = {"nsx": "n1", "nsy": "n2"}
        counts = {"nsx": 0, "nsy": 0}

        def side_effect(*args, **kwargs):
            ns = kwargs.get("namespace")
            counts[ns] += 1
            return f"{prefix[ns]}-{counts[ns]}"

        mock = mocker.patch.object(driver, "insert_vector", side_effect=side_effect)

        artifacts = {"nsx": [TextArtifact("a"), TextArtifact("b")], "nsy": [TextArtifact("c")]}
        result = driver.insert_collection(artifacts)

        assert isinstance(result, dict)
        assert set(result.keys()) == {"nsx", "nsy"}
        # Per-namespace order is preserved by BaseVectorStoreDriver utilities
        assert result["nsx"] == ["n1-1", "n1-2"]
        assert result["nsy"] == ["n2-1"]
        assert mock.call_count == 3
        # Validate counts per namespace without assuming cross-namespace call order
        namespaces = [c.kwargs.get("namespace") for c in mock.call_args_list]
        assert namespaces.count("nsx") == 2
        assert namespaces.count("nsy") == 1

    def test_upsert(self, driver):
        namespace = driver.upsert(TextArtifact(id="foo1", value="foobar"))

        assert len(driver.entries) == 1
        assert list(driver.entries.keys())[0] == namespace

        driver.upsert(TextArtifact(id="foo1", value="foobar"))

        assert len(driver.entries) == 1

        driver.upsert(TextArtifact(id="foo2", value="foobar2"))

        assert len(driver.entries) == 2

    def test_upsert_multiple(self, driver):
        driver.upsert_collection({"foo": [TextArtifact("foo")], "bar": [TextArtifact("bar")]})

        foo_entries = driver.load_entries(namespace="foo")
        bar_entries = driver.load_entries(namespace="bar")

        assert len(driver.entries) == 2
        assert foo_entries[0].to_artifact().value == "foo"
        assert bar_entries[0].to_artifact().value == "bar"

    def test_query(self, driver):
        vector_id = driver.upsert(TextArtifact("foobar"), namespace="test-namespace")

        assert len(driver.query("foobar")) == 1
        assert len(driver.query("foobar", namespace="bad-namespace")) == 0
        assert len(driver.query("foobar", namespace="test-namespace")) == 1
        assert driver.query("foobar")[0].vector == []
        assert driver.query("foobar", include_vectors=True)[0].vector == [0, 1]
        assert driver.query("foobar")[0].to_artifact().value == "foobar"
        assert driver.query("foobar")[0].id == vector_id

    def test_load_entry(self, driver):
        vector_id = driver.upsert(TextArtifact("foobar"), namespace="test-namespace")

        assert driver.load_entry(vector_id, namespace="test-namespace").id == vector_id

    def test_load_entries(self, driver):
        driver.upsert(TextArtifact("foobar 1"), namespace="test-namespace-1")
        driver.upsert(TextArtifact("foobar 2"), namespace="test-namespace-1")
        driver.upsert(TextArtifact("foobar 3"), namespace="test-namespace-2")

        assert len(driver.load_entries()) == 3
        assert len(driver.load_entries(namespace="test-namespace-1")) == 2
        assert len(driver.load_entries(namespace="test-namespace-2")) == 1

    def test_load_artifacts(self, driver):
        driver.upsert(TextArtifact("foobar 1"), namespace="test-namespace-1")
        driver.upsert(TextArtifact("foobar 2"), namespace="test-namespace-1")
        driver.upsert(TextArtifact("foobar 3"), namespace="test-namespace-2")

        assert len(driver.load_artifacts()) == 3
        assert len(driver.load_artifacts(namespace="test-namespace-1")) == 2
        assert len(driver.load_artifacts(namespace="test-namespace-2")) == 1

    def test_does_entry_exist_exception(self, driver):
        with patch.object(driver, "load_entry", side_effect=Exception):
            assert driver.does_entry_exist("does_not_exist") is False
