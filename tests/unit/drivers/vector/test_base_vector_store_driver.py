from abc import ABC, abstractmethod
from unittest.mock import patch

import pytest

from griptape.artifacts import BaseArtifact, TextArtifact
from griptape.drivers.vector import BaseVectorStoreDriver


class TestBaseVectorStoreDriver(ABC):
    @pytest.fixture()
    @abstractmethod
    def driver(self, *args, **kwargs) -> BaseVectorStoreDriver: ...

    def test_upsert(self, driver):
        namespace = driver.upsert(TextArtifact(id="foo1", value="foobar"))

        assert len(driver.entries) == 1
        assert list(driver.entries.keys())[0] == namespace

        driver.upsert(TextArtifact(id="foo1", value="foobar"))

        assert len(driver.entries) == 1

        driver.upsert(TextArtifact(id="foo2", value="foobar2"))

        assert len(driver.entries) == 2

    def test_insert(self, driver):
        id1 = driver.insert(TextArtifact(value="foobar"))

        assert driver.load_entry(id1).id == id1

        id2 = driver.insert(TextArtifact(value="foobar"))

        assert id1 != id2
        assert len(driver.entries) == 2

    def test_insert_collection_list(self, driver):
        ids = driver.insert_collection([TextArtifact("foo"), TextArtifact("foo")])

        assert len(set(ids)) == 2
        assert len(driver.entries) == 2

    def test_insert_collection_dict(self, driver):
        ids = driver.insert_collection(
            {"foo": [TextArtifact("foo"), TextArtifact("foo")], "bar": [TextArtifact("bar")]}
        )

        assert len(set(ids["foo"])) == 2
        assert len(driver.load_entries(namespace="foo")) == 2
        assert len(driver.load_entries(namespace="bar")) == 1

    def test_upsert_multiple(self, driver):
        driver.upsert_collection({"foo": [TextArtifact("foo")], "bar": [TextArtifact("bar")]})

        foo_entries = driver.load_entries(namespace="foo")
        bar_entries = driver.load_entries(namespace="bar")

        assert len(driver.entries) == 2
        assert foo_entries[0].to_artifact().value == "foo"
        assert bar_entries[0].to_artifact().value == "bar"

    def test_upsert_vectors(self, driver):
        entries = [
            BaseVectorStoreDriver.Entry(
                id="foo", vector=[0, 1], meta={"artifact": TextArtifact("foo").to_json()}, namespace="ns1"
            ),
            BaseVectorStoreDriver.Entry(
                id="bar", vector=[1, 0], meta={"artifact": TextArtifact("bar").to_json()}, namespace="ns2"
            ),
        ]

        assert driver.upsert_vectors(entries) == ["foo", "bar"]
        assert driver.load_entry("foo", namespace="ns1").to_artifact().value == "foo"
        assert driver.load_entry("bar", namespace="ns2").vector == [1, 0]

    def test_upsert_vectors_empty(self, driver):
        assert driver.upsert_vectors([]) == []
        assert driver.load_entries() == []

    @pytest.mark.parametrize("method", ["upsert_collection", "insert_collection"])
    def test_collection_list_upserts_in_one_call(self, driver, mocker, method):
        spy = mocker.spy(driver, "upsert_vectors")

        ids = getattr(driver, method)([TextArtifact("foo"), TextArtifact("bar")])

        assert spy.call_count == 1
        entries = spy.call_args.args[0]
        assert [entry.to_artifact().value for entry in entries] == ["foo", "bar"]
        assert [entry.namespace for entry in entries] == [None, None]
        assert ids == [entry.id for entry in entries]

    @pytest.mark.parametrize("method", ["upsert_collection", "insert_collection"])
    def test_collection_dict_upserts_in_one_call(self, driver, mocker, method):
        spy = mocker.spy(driver, "upsert_vectors")

        ids = getattr(driver, method)({"foo": [TextArtifact("a"), TextArtifact("b")], "bar": [TextArtifact("c")]})

        assert spy.call_count == 1
        entries = spy.call_args.args[0]
        assert [(entry.namespace, entry.to_artifact().value) for entry in entries] == [
            ("foo", "a"),
            ("foo", "b"),
            ("bar", "c"),
        ]
        assert ids == {"foo": [entries[0].id, entries[1].id], "bar": [entries[2].id]}

    @pytest.mark.parametrize("method", ["upsert_collection", "insert_collection"])
    def test_collection_empty(self, driver, method):
        assert getattr(driver, method)([]) == []
        assert getattr(driver, method)({}) == {}
        assert driver.load_entries() == []

    def test_upsert_collection_uses_content_hash_ids(self, driver):
        ids = driver.upsert_collection({"foo": [TextArtifact("a"), TextArtifact("b")]})

        assert ids == {"foo": [driver._get_default_vector_id("a"), driver._get_default_vector_id("b")]}

    def test_upsert_collection_duplicate_artifacts(self, driver):
        ids = driver.upsert_collection([TextArtifact("foo"), TextArtifact("foo")])

        assert ids[0] == ids[1]
        assert len(driver.load_entries()) == 1

    @pytest.mark.parametrize("method", ["upsert_collection", "insert_collection"])
    def test_collection_meta_and_kwargs(self, driver, mocker, method):
        spy = mocker.spy(driver, "upsert_vector")

        getattr(driver, method)([TextArtifact("foo")], meta={"foo": "bar"}, baz="qux")

        assert spy.call_args.kwargs["meta"]["foo"] == "bar"
        assert BaseArtifact.from_json(spy.call_args.kwargs["meta"]["artifact"]).value == "foo"
        assert spy.call_args.kwargs["baz"] == "qux"

    @pytest.mark.parametrize("method", ["upsert_collection", "insert_collection"])
    def test_collection_embedding_error_writes_nothing(self, driver, method):
        def mock_output(chunk):
            if chunk == "bad":
                raise ValueError("embedding failed")
            return [0, 1]

        driver.embedding_driver.mock_output = mock_output

        with pytest.raises(ValueError, match="embedding failed"):
            getattr(driver, method)([TextArtifact("good"), TextArtifact("bad")])

        assert driver.load_entries() == []

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
