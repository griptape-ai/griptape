from __future__ import annotations

import mimetypes

import filetype


def get_mime_type(file_path_or_bytes: str | bytes) -> str:
    """Attempt to determine the MIME type of a file or bytes.

    Will first attempt to use the `filetype` library to determine the MIME type.
    If the library cannot determine the MIME type (data missing magic bytes), we have two options:
    If the user provided bytes, we can try to determine if the bytes represent text data. Otherwise, we default to
    "application/octet-stream".

    If the user provided a filepath, we can try using the built-in `mimetypes` package to guess the MIME type.
    In practice, it's unlikely that this will succeed in cases where `filetype` fails, but it's a good fallback.

    Args:
        file_path_or_bytes: The path to the file or the bytes to check.

    Returns: The MIME type of the file or bytes.
    """
    filetype_guess = filetype.guess(file_path_or_bytes)

    if filetype_guess is None:
        if isinstance(file_path_or_bytes, bytes):
            if _is_text(file_path_or_bytes):
                return "text/plain"
            else:
                return "application/octet-stream"
        type_, _ = mimetypes.guess_type(file_path_or_bytes)
        if type_ is None:
            return "application/octet-stream"
        else:
            return type_
    else:
        return filetype_guess.mime


def _is_text(data: bytes) -> bool:
    """Heuristic check to determine if bytes represent text data.

    https://github.com/h2non/filetype.py/issues/30

    Args:
        data: The bytes to check.

    Returns: True if the bytes represent text data, False otherwise.
    """
    try:
        text = data.decode("utf-8")
        return all(c.isprintable() or c.isspace() for c in text)
    except UnicodeDecodeError:
        return False
