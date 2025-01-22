from __future__ import annotations

import pytest

from griptape.artifacts import BaseArtifact, TextArtifact
from griptape.drivers.file_manager import BaseFileManagerDriver


class MockFileManagerDriver(BaseFileManagerDriver):
    @property
    def workdir(self) -> str:
        return self._workdir

    @workdir.setter
    def workdir(self, value: str) -> None:
        self._workdir = value

    def try_list_files(self, path: str) -> list[str]:
        return ["foo", "bar"]

    def try_save_file(self, path: str, value: bytes) -> str:
        assert path == "foo"
        assert BaseArtifact.from_json(value.decode()).value == TextArtifact(value="value").value

        return "mock_save_location"

    def try_load_file(self, path: str) -> bytes:
        assert path == "foo"

        return TextArtifact(value="value").to_json().encode()


class TestBaseFileManagerDriver:
    @pytest.fixture()
    def driver(self):
        return MockFileManagerDriver(workdir="/")

    def test_load_artifact(self, driver):
        response = driver.load_artifact("foo")

        assert response.value == "value"

    def test_save_artifact(self, driver):
        response = driver.save_artifact("foo", TextArtifact(value="value"))

        assert response.value == "Successfully saved artifact at: mock_save_location"

    def test_workdir(self, driver):
        assert driver.workdir == "/"
        driver.workdir = "/new"
        assert driver.workdir == "/new"
