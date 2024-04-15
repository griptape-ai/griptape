import griptape.utils as utils
from concurrent import futures


def load_file(path: str) -> bytes:
    """Load a file from the given path and return its content as bytes.

    Args:
        path (str): The path to the file to load.

    Returns:
        The content of the file.
    """
    with open(path, "rb") as f:
        return f.read()


def load_files(paths: list[str]) -> dict[str, bytes]:
    """Load multiple files concurrently and return a dictionary of their content.

    Args:
        paths: The paths to the files to load.

    Returns:
        A dictionary where the keys are a hash of the path and the values are the content of the files.
    """

    futures_executor = futures.ThreadPoolExecutor()

    return utils.execute_futures_dict(
        {utils.str_to_hash(str(path)): futures_executor.submit(load_file, path) for path in paths}
    )
