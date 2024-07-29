import os
from pathlib import Path

import pytest


@pytest.fixture()
def path_from_resource_path():
    def create_source(resource_path: str) -> Path:
        return Path(os.path.join(os.path.abspath(os.path.dirname(__file__)), "../../resources", resource_path))

    return create_source
