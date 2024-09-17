from abc import ABC, abstractmethod
from unittest.mock import patch

import pytest

from griptape.artifacts import TextArtifact


class BaseLocalVectorStoreDriver(ABC):
    @pytest.fixture()
    @abstractmethod
    def driver(self): ...

    def test_upsert(self, driver):
        namespace = driver.upsert_text_artifact(TextArtifact(id="foo1", value="foobar"))

        assert len(driver.entries) == 1
        assert list(driver.entries.keys())[0] == namespace

        driver.upsert_text_artifact(TextArtifact(id="foo1", value="foobar"))

        assert len(driver.entries) == 1

        driver.upsert_text_artifact(TextArtifact(id="foo2", value="foobar2"))

        assert len(driver.entries) == 2

    def test_upsert_multiple(self, driver):
        driver.upsert_text_artifacts({"foo": [TextArtifact("foo")], "bar": [TextArtifact("bar")]})

        foo_entries = driver.load_entries(namespace="foo")
        bar_entries = driver.load_entries(namespace="bar")

        assert len(driver.entries) == 2
        assert foo_entries[0].to_artifact().value == "foo"
        assert bar_entries[0].to_artifact().value == "bar"

    def test_query(self, driver):
        vector_id = driver.upsert_text_artifact(TextArtifact("foobar"), namespace="test-namespace")

        assert len(driver.query("foobar")) == 1
        assert len(driver.query("foobar", namespace="bad-namespace")) == 0
        assert len(driver.query("foobar", namespace="test-namespace")) == 1
        assert driver.query("foobar")[0].vector == []
        assert driver.query("foobar", include_vectors=True)[0].vector == [0, 1]
        assert driver.query("foobar")[0].to_artifact().value == "foobar"
        assert driver.query("foobar")[0].id == vector_id

    def test_load_entry(self, driver):
        vector_id = driver.upsert_text_artifact(TextArtifact("foobar"), namespace="test-namespace")

        assert driver.load_entry(vector_id, namespace="test-namespace").id == vector_id

    def test_load_entries(self, driver):
        driver.upsert_text_artifact(TextArtifact("foobar 1"), namespace="test-namespace-1")
        driver.upsert_text_artifact(TextArtifact("foobar 2"), namespace="test-namespace-1")
        driver.upsert_text_artifact(TextArtifact("foobar 3"), namespace="test-namespace-2")

        assert len(driver.load_entries()) == 3
        assert len(driver.load_entries(namespace="test-namespace-1")) == 2
        assert len(driver.load_entries(namespace="test-namespace-2")) == 1

    def test_load_artifacts(self, driver):
        driver.upsert_text_artifact(TextArtifact("foobar 1"), namespace="test-namespace-1")
        driver.upsert_text_artifact(TextArtifact("foobar 2"), namespace="test-namespace-1")
        driver.upsert_text_artifact(TextArtifact("foobar 3"), namespace="test-namespace-2")

        assert len(driver.load_artifacts()) == 3
        assert len(driver.load_artifacts(namespace="test-namespace-1")) == 2
        assert len(driver.load_artifacts(namespace="test-namespace-2")) == 1

    def test_does_entry_exist_exception(self, driver):
        with patch.object(driver, "load_entry", side_effect=Exception):
            assert driver.does_entry_exist("does_not_exist") is False
