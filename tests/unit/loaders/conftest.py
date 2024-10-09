import os
from io import BytesIO, StringIO
from pathlib import Path

import pytest


@pytest.fixture()
def path_from_resource_path():
    def create_source(resource_path: str) -> Path:
        return Path(os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../resources", resource_path))

    return create_source


@pytest.fixture()
def bytes_from_resource_path(path_from_resource_path):
    def create_source(resource_path: str) -> BytesIO:
        return BytesIO(Path(path_from_resource_path(resource_path)).read_bytes())

    return create_source


@pytest.fixture()
def str_from_resource_path(path_from_resource_path):
    def test_csv_str(resource_path: str) -> StringIO:
        return StringIO(Path(path_from_resource_path(resource_path)).read_text())

    return test_csv_str
