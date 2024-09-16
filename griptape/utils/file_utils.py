from __future__ import annotations

import mimetypes

import filetype


def get_mime_type(path_or_bytes: str | bytes) -> str:
    filetype_guess = filetype.guess(path_or_bytes)

    if filetype_guess is None:
        if isinstance(path_or_bytes, str):
            type_, _ = mimetypes.guess_type(path_or_bytes)
            if type_ is None:
                return "application/octet-stream"
            else:
                return type_
        else:
            raise ValueError("Could not guess the file type, try passing a path instead of bytes")
    else:
        return filetype_guess.mime
