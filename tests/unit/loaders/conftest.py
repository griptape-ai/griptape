import os
from pathlib import Path
from typing import IO

import pytest


@pytest.fixture
def path_from_resource_path():
    def create_source(resource_path: str) -> Path:
        return Path(os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../resources", resource_path))

    return create_source


@pytest.fixture
def bytes_from_resource_path(path_from_resource_path):
    def create_source(resource_path: str) -> bytes:
        with open(path_from_resource_path(resource_path), "rb") as f:
            return f.read()

    return create_source


@pytest.fixture
def str_from_resource_path(path_from_resource_path):
    def test_csv_str(resource_path: str) -> str:
        with open(path_from_resource_path(resource_path)) as f:
            return f.read()

    return test_csv_str


@pytest.fixture
def binary_io_from_resource_path(path_from_resource_path):
    files_opened = []

    def create_source(resource_path: str) -> IO:
        f = open(path_from_resource_path(resource_path), "rb")
        files_opened.append(f)
        return f

    yield create_source

    for f in files_opened:
        f.close()


@pytest.fixture
def text_io_from_resource_path(path_from_resource_path):
    files_opened = []

    def create_source(resource_path: str) -> IO:
        f = open(path_from_resource_path(resource_path))
        files_opened.append(f)
        return f

    yield create_source

    for f in files_opened:
        f.close()
