__path__ = __import__("pkgutil").extend_path(__path__, __name__)

import os

PACKAGE_ABS_PATH = os.path.dirname(os.path.abspath(__file__))


def abs_path(path: str) -> str:
    return os.path.join(PACKAGE_ABS_PATH, path)


__all__ = [
    "PACKAGE_ABS_PATH"
]
