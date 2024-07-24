from __future__ import annotations

from concurrent import futures
from pathlib import Path
from typing import Optional

import griptape.utils as utils


def load_file(path: str) -> bytes:
    """Load a file from the given path and return its content as bytes.

    Args:
        path (str): The path to the file to load.

    Returns:
        The content of the file.
    """
    return Path(path).read_bytes()


def load_files(paths: list[str], futures_executor: Optional[futures.ThreadPoolExecutor] = None) -> dict[str, bytes]:
    """Load multiple files concurrently and return a dictionary of their content.

    Args:
        paths: The paths to the files to load.
        futures_executor: The executor to use for concurrent loading. If None, a new ThreadPoolExecutor will be created.

    Returns:
        A dictionary where the keys are a hash of the path and the values are the content of the files.
    """
    if futures_executor is None:
        futures_executor = futures.ThreadPoolExecutor()

    with futures_executor as executor:
        return utils.execute_futures_dict(
            {utils.str_to_hash(str(path)): executor.submit(load_file, path) for path in paths},
        )
